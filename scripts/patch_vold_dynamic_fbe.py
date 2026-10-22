#!/usr/bin/env python3
"""Patch TWRP vold for runtime FBE v1/v2 decryption.

TWRP copies the installed ROM's fstab to /etc/additional.fstab.  vold must use
that fstab for /data and /metadata, not the recovery fallback, otherwise a
ROM's FBE version/metadata flags are lost.  As a second safety net, vold also
reads the policy actually installed on /data/misc and overrides the fstab
version when a ROM update changed the layout without reformatting data.
"""

import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_vold_dynamic_fbe.py <path/to/FsCrypt.cpp>")

    path = Path(sys.argv[1])
    src = path.read_text()

    # fscrypt_policy_get_struct() and the fscrypt_policy union live here.
    if '#include "fscrypt_policy.h"' not in src:
        needle = '#include "fscrypt-common.h"'
        if needle not in src:
            raise SystemExit(f"expected fscrypt-common.h include in {path}")
        src = src.replace(needle, needle + '\n#include "fscrypt_policy.h"', 1)

    if '#include <cstring>' not in src:
        anchor = ('#include "fscrypt_policy.h"'
                  if '#include "fscrypt_policy.h"' in src
                  else '#include "fscrypt-common.h"')
        if anchor not in src:
            raise SystemExit(f"expected an fscrypt include in {path}")
        src = src.replace(anchor, anchor + '\n#include <cstring>', 1)

    # Use the installed ROM's fstab for the FBE key options.  This is the
    # file TWRP creates from /vendor/etc/fstab.<hardware>.
    old_fstab = '''    if (fstab_default.empty()) {
        if (!ReadDefaultFstab(&fstab_default)) {
            PLOG(ERROR) << "Failed to open default fstab";
            return false;
        }
    }
    auto entry = GetEntryForMountPoint(&fstab_default, DATA_MNT_POINT);'''
    new_fstab = '''    if (fstab_default.empty() && !ReadDefaultFstab(&fstab_default)) {
        // Keep going: the additional fstab may still be usable.
        PLOG(ERROR) << "Failed to open default fstab";
    }
    android::fs_mgr::Fstab rom_fstab;
    android::fs_mgr::Fstab* fstab = &fstab_default;
    if (access("/etc/additional.fstab", R_OK) == 0 &&
        ReadFstabFromFile("/etc/additional.fstab", &rom_fstab)) {
        fstab = &rom_fstab;
        LOG(INFO) << "FBE: using installed ROM fstab /etc/additional.fstab";
    }
    if (fstab->empty()) {
        LOG(ERROR) << "No fstab entries available for " << DATA_MNT_POINT;
        return false;
    }
    auto entry = GetEntryForMountPoint(fstab, DATA_MNT_POINT);'''
    if 'FBE: using installed ROM fstab' not in src:
        if old_fstab not in src:
            raise SystemExit(f"expected get_data_file_encryption_options fstab block in {path}")
        src = src.replace(old_fstab, new_fstab, 1)
        print("patched fstab selection")

    # Check the real on-disk policy.  A ROM update can change the fstab
    # version without reformatting /data.  If the policy ioctl is not
    # available, the legacy v1 dirent format contains a comma while v2
    # base64url names do not.
    old_parse = '''    if (!ParseOptions(entry->encryption_options, options)) {
        LOG(ERROR) << "Unable to parse encryption options for " << DATA_MNT_POINT ": "
                   << entry->encryption_options;
        return false;
    }'''
    new_parse = old_parse + '''
    bool detected_v1 = false;
    bool detected = false;
    int installed_version = -1;
    fscrypt_policy installed_policy{};
    // Cache the normalized vold version (1 or 2), not the raw kernel policy
    // version.  FSCRYPT_POLICY_V1 is 0 in the kernel UAPI, while
    // EncryptionOptions::version uses 1 for v1.  Passing 0 to installKey()
    // makes it reject the key with "Invalid encryption policy version: 0".
    static int cached_policy_version = -1;
    if (cached_policy_version == 1 || cached_policy_version == 2) {
        installed_version = cached_policy_version;
        detected = true;
    } else if (fscrypt_policy_get_struct("/data/misc", &installed_policy)) {
        if (installed_policy.version == FSCRYPT_POLICY_V1) {
            installed_version = 1;
        } else if (installed_policy.version == FSCRYPT_POLICY_V2) {
            installed_version = 2;
        }
        detected = installed_version != -1;
    } else {
        DIR* dir = opendir("/data/misc");
        if (dir != nullptr) {
            struct dirent* de;
            while ((de = readdir(dir)) != nullptr) {
                if (de->d_name[0] == '.') continue;
                // Legacy v1 encrypted dirents contain a comma; v2 base64url
                // names do not.
                installed_version = std::strchr(de->d_name, ',') != nullptr ? 1 : 2;
                detected = true;
                break;
            }
            closedir(dir);
        }
    }
    if (detected) {
        if (options->version != installed_version) {
            LOG(INFO) << "FBE: installed /data policy is v"
                      << installed_version
                      << "; overriding fstab policy v"
                      << static_cast<int>(options->version);
        }
        options->version = installed_version;
        detected_v1 = installed_version == 1;
        cached_policy_version = installed_version;
    }
    if (detected_v1) {
        // Hardware-wrapped keys and IV_INO_LBLK_32 are v2-only features.
        options->use_hw_wrapped_key = false;
        options->flags &= ~FSCRYPT_POLICY_FLAG_IV_INO_LBLK_32;
    }'''
    if 'FBE: installed /data policy is v' not in src:
        if old_parse not in src:
            raise SystemExit(f"expected ParseOptions block in {path}")
        src = src.replace(old_parse, new_parse, 1)
        print("patched installed-policy detection")

    # The wrapped-key choice must come from the same fstab entry that was
    # parsed, and must never be enabled for a detected v1 policy.
    old_wrapped = '''    if (options->version == 1 || !retry) {
        options->use_hw_wrapped_key =
            GetEntryForMountPoint(&fstab_default, DATA_MNT_POINT)->fs_mgr_flags.wrapped_key;
    }'''
    new_wrapped = '''    if (options->version == 1 || !retry) {
        options->use_hw_wrapped_key = entry->fs_mgr_flags.wrapped_key;
    }
    if (detected_v1) {
        options->use_hw_wrapped_key = false;
    }'''
    if 'options->use_hw_wrapped_key = entry->fs_mgr_flags.wrapped_key;' not in src:
        if old_wrapped not in src:
            raise SystemExit(f"expected wrapped-key block in {path}")
        src = src.replace(old_wrapped, new_wrapped, 1)
        print("patched wrapped-key selection")

    # A v1 policy can never use hardware-wrapped keys.  Do not let the generic
    # retry path toggle one on after a v1 install failure; that only produces a
    # misleading keymaster error and masks the real failure.
    old_retry = '''        if (retry) {
            printf("Trying %s wrappedkey\\n", options.use_hw_wrapped_key ? "without" : "with");
            GetEntryForMountPoint(&fstab_default, DATA_MNT_POINT)->fs_mgr_flags.wrapped_key =
                options.use_hw_wrapped_key = !options.use_hw_wrapped_key;
            retry = false;
            goto install;
        }'''
    new_retry = '''        if (retry && options.version != 1) {
            printf("Trying %s wrappedkey\\n", options.use_hw_wrapped_key ? "without" : "with");
            GetEntryForMountPoint(&fstab_default, DATA_MNT_POINT)->fs_mgr_flags.wrapped_key =
                options.use_hw_wrapped_key = !options.use_hw_wrapped_key;
            retry = false;
            goto install;
        }'''
    if 'if (retry && options.version != 1)' not in src:
        if old_retry not in src:
            raise SystemExit(f"expected wrapped-key retry block in {path}")
        src = src.replace(old_retry, new_retry, 1)
        print("patched v1 wrapped-key retry")

    path.write_text(src)


if __name__ == "__main__":
    main()
