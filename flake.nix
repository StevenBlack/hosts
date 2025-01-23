{
  description = "Unified hosts file with base extensions.";
  outputs = { self, nixpkgs, ... }@inputs:
    let
      forAllSystems = nixpkgs.lib.genAttrs nixpkgs.lib.platforms.unix;

      nixpkgsFor = forAllSystems (system: import nixpkgs {
        inherit system;
      });
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
              in lib.mkAfter (orig + (lib.optionalString cfg.enableIPv6 ("\n" + ipv6)));
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
    };
}
