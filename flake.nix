{
  description = "Unified hosts file with base extensions.";
  outputs =
    {
      self,
      nixpkgs,
      ...
    }:
    let
      forAllSystems = nixpkgs.lib.genAttrs nixpkgs.lib.platforms.unix;
      nixpkgsFor = forAllSystems (system: import nixpkgs { inherit system; });
    in
    {
      nixosModule =
        { config, ... }:
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
                orig = builtins.readFile (
                  "${self}/" + (lib.optionalString (alternatesList != [ ]) alternatesPath) + "hosts"
                );
                filterHosts = text:
                  builtins.concatStringsSep "\n"
                    (builtins.filter
                      (line:
                        let first = builtins.elemAt (lib.splitString " " line) 0;
                        in !(lib.hasInfix "%" first)
                      )
                      (lib.splitString "\n" text)
                    );
                filtered = filterHosts orig;
                ipv6 = builtins.replaceStrings [ "0.0.0.0" ] [ "::" ] filtered;
              in
              lib.mkAfter (filtered + (lib.optionalString cfg.enableIPv6 ("\n" + ipv6)));
          };
        };

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgsFor.${system};
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              nixfmt
              (python3.withPackages (
                pythonPackages: with pythonPackages; [
                  flake8
                  requests
                ]
              ))
            ];
          };
        }
      );

      packages = forAllSystems (system: {
        unbound = nixpkgsFor.${system}.callPackage ./unbound.nix { };
      });
    };
}
