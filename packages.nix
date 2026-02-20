pkgs:
let
  lib = pkgs.lib;
  toUnboundConf = (
    file:
    lib.strings.concatMapStringsSep "\n" (
      line:
      if (lib.strings.hasPrefix "#" line) || (line == "") then
        line
      else
        let
          splitLine = (lib.strings.splitString " " line);
          address = builtins.elemAt splitLine 0;
          domain = builtins.elemAt splitLine 1;
        in
        ''
          local-zone: "${domain}" redirect
          local-data: "${domain} A ${address}"
        ''
    ) (lib.strings.splitString "\n" (builtins.readFile file))
  );
  files =
    lib.trivial.pipe (builtins.readDir ./alternates) [
      (lib.filterAttrs (
        name: type: type == "directory" && (builtins.length (lib.strings.splitString "-" name)) == 1 # select only non-combined filter lists
      ))
      (lib.attrsets.mapAttrs (name: _: ./alternates/${name}/hosts))
      (lib.attrsets.filterAttrs (name: file: builtins.pathExists file))
    ]
    // {
      all = ./hosts;
    };
in
lib.attrsets.mapAttrs (
  name: file:
  pkgs.writeTextFile {
    inherit name;
    text = toUnboundConf file;
  }
) files
