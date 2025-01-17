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
        with nixpkgs.lib;
        let
          cfg = config.networking.stevenBlackHosts;
          alternatesList = (if cfg.blockFakenews then [ "fakenews" ] else []) ++
                           (if cfg.blockGambling then [ "gambling" ] else []) ++
                           (if cfg.blockPorn then [ "porn" ] else []) ++
                           (if cfg.blockSocial then [ "social" ] else []);
          alternatesPath = "alternates/" + builtins.concatStringsSep "-" alternatesList + "/";
        in
        {
          options.networking.stevenBlackHosts = {
            enable = mkEnableOption "Steven Black's hosts file";
            enableIPv6 = mkEnableOption "IPv6 rules" // {
              default = config.networking.enableIPv6;
            };
            blockFakenews = mkEnableOption "Additionally block fakenews hosts.";
            blockGambling = mkEnableOption "Additionally block gambling hosts.";
            blockPorn = mkEnableOption "Additionally block porn hosts.";
            blockSocial = mkEnableOption "Additionally block social hosts.";
          };
          config = mkIf cfg.enable {
            networking.extraHosts =
              let
                orig = builtins.readFile ("${self}/" + (if alternatesList != [] then alternatesPath else "") + "hosts");
                ipv6 = builtins.replaceStrings [ "0.0.0.0" ] [ "::" ] orig;
              in orig + (optionalString cfg.enableIPv6 ("\n" + ipv6));
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
