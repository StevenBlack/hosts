pkgs:
let
  lib = pkgs.lib;
  toUnboundConf = (
    file:
    lib.strings.concatMapStrings (
      line:
      let
        splitLine = lib.strings.splitString " " line;
        address = builtins.elemAt splitLine 0;
      in
      lib.optionalString (address == "0.0.0.0") ''
        local-zone: "${builtins.elemAt splitLine 1}" refuse
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
{
  raw = lib.attrsets.mapAttrs (
    name: file:
    builtins.path {
      inherit name;
      path = file;
    }
  ) files;
  unbound = lib.attrsets.mapAttrs (
    name: file:
    pkgs.writeTextFile {
      inherit name;
      text = toUnboundConf file;
    }
  ) files;
}
