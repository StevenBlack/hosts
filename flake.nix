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
            enable = mkEnableOption "Use Steven Black's hosts file as extra hosts.";
            blockFakenews = mkEnableOption "Additionally block fakenews hosts.";
            blockGambling = mkEnableOption "Additionally block gambling hosts.";
            blockPorn = mkEnableOption "Additionally block porn hosts.";
            blockSocial = mkEnableOption "Additionally block social hosts.";
          };
          config = mkIf cfg.enable {
            networking.extraHosts =
              builtins.readFile (
                "${self}/" + (if alternatesList != [] then alternatesPath else "") + "hosts"
              );
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
