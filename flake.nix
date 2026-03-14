{
  description = "Unified hosts file with base extensions.";
  outputs = { self, nixpkgs, ... }@inputs:
    let
      forAllSystems = nixpkgs.lib.genAttrs nixpkgs.lib.platforms.unix;

      nixpkgsFor = forAllSystems (system: import nixpkgs {
        inherit system;
      });

      toUnboundConf = (
        file:
        nixpkgs.lib.strings.concatMapStringsSep "\n" (
            line:
            if (nixpkgs.lib.strings.hasPrefix "#" line) || (line == "") then
              line
            else
              let
                split_line = (nixpkgs.lib.strings.splitString " " line);
                address = builtins.elemAt split_line 0;
                domain = builtins.elemAt split_line 1;
              in
              ''
                local-zone: "${domain}" redirect
                local-data: "${domain} A ${address}"
              ''
          ) (nixpkgs.lib.strings.splitString "\n" (builtins.readFile file))
      );
    in
    {
      nixosModule = { config, ... }:
        let
          inherit (nixpkgs) lib;
          cfg = config.networking.stevenBlackHosts;
          alternatesList =
            (lib.optional cfg.blockFakenews "fakenews")
            ++ (lib.optional cfg.blockGambling "gambling")
            ++ (lib.optional cfg.blockPorn "porn")
            ++ (lib.optional cfg.blockSocial "social");
          alternatesPath = "alternates/" + builtins.concatStringsSep "-" alternatesList + "/";
        in
        {
          options.networking.stevenBlackHosts = {
            enable = lib.mkEnableOption "Steven Black's hosts file";
            enableIPv6 = lib.mkEnableOption "IPv6 rules" // {
              default = config.networking.enableIPv6;
              defaultText = lib.literalExpression "config.networking.enableIPv6";
            };
            blockFakenews = lib.mkEnableOption "fakenews hosts entries";
            blockGambling = lib.mkEnableOption "gambling hosts entries";
            blockPorn = lib.mkEnableOption "porn hosts entries";
            blockSocial = lib.mkEnableOption "social hosts entries";
          };
          config = lib.mkIf cfg.enable {
            networking.extraHosts =
              let
                orig = builtins.readFile ("${self}/" + (lib.optionalString (alternatesList != []) alternatesPath) + "hosts");
                ipv6 = builtins.replaceStrings [ "0.0.0.0" ] [ "::" ] orig;
              in
              lib.mkAfter (orig + (lib.optionalString cfg.enableIPv6 ("\n" + ipv6)));
          };
        };

      devShells = forAllSystems (system:
        let pkgs = nixpkgsFor.${system}; in
        {
          default = pkgs.mkShell {
            buildInputs = with pkgs; [
              python3
              python3Packages.flake8
              python3Packages.requests
            ];
          };
        });

      overlays.default = (
        final: prev: {
          unboundconfs = prev.lib.makeScope prev.pkgs.newScope (newscope: self.packages.${prev.system});
        }
      );

      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgsFor.${system};
          dir = ./alternates;
          lists =
            pkgs.lib.trivial.pipe (builtins.readDir ./alternates) [
              (pkgs.lib.filterAttrs (k: v: (builtins.length (pkgs.lib.strings.splitString "-" k)) == 1 && v == "directory")) # select only non-combined filter lists
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
      );
    };
}
