{
  description = "Unified hosts file with base extensions.";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  outputs = { self, nixpkgs, flake-utils }: {
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
  } // flake-utils.lib.eachDefaultSystem
    (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            python3Packages.flake8
            python3Packages.requests
          ];
        };
      }
    );
}
