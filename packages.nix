pkgs:
let
  toUnboundConf = (
    file:
    pkgs.lib.strings.concatMapStringsSep "\n" (
      line:
      if (pkgs.lib.strings.hasPrefix "#" line) || (line == "") then
        line
      else
        let
          split_line = (pkgs.lib.strings.splitString " " line);
          address = builtins.elemAt split_line 0;
          domain = builtins.elemAt split_line 1;
        in
        ''
          local-zone: "${domain}" redirect
          local-data: "${domain} A ${address}"
        ''
    ) (pkgs.lib.strings.splitString "\n" (builtins.readFile file))
  );
  dir = ./alternates;
  lists =
    pkgs.lib.trivial.pipe (builtins.readDir ./alternates) [
      (pkgs.lib.filterAttrs (
        k: v: (builtins.length (pkgs.lib.strings.splitString "-" k)) == 1 && v == "directory"
      )) # select only non-combined filter lists
      (pkgs.lib.attrsets.mapAttrs (k: v: dir + "/${k}/hosts"))
      (pkgs.lib.attrsets.filterAttrs (k: v: builtins.pathExists v))
    ]
    // {
      all = ./hosts;
    };
in
pkgs.lib.attrsets.mapAttrs (
  k: v:
  pkgs.writeTextFile {
    name = k;
    text = toUnboundConf v;
  }
) lists
