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
          inherit (nixpkgs) lib;
          cfg = config.networking.stevenBlackHosts;
          alternatesList = (if cfg.blockFakenews then [ "fakenews" ] else []) ++
                           (if cfg.blockGambling then [ "gambling" ] else []) ++
                           (if cfg.blockPorn then [ "porn" ] else []) ++
                           (if cfg.blockSocial then [ "social" ] else []);
          alternatesPath = "/alternates/" + builtins.concatStringsSep "-" alternatesList;
          orig = builtins.readFile (
            self.outPath + (if alternatesList != [ ] then alternatesPath else "") + "/hosts"
          );
          filtered =
            if cfg.enableIPv6 then
              orig
            else
              lib.concatStringsSep "\n" (
                lib.filter (line: !(lib.strings.hasPrefix "::" line)) (lib.strings.splitString "\n" orig)
              );
        in
        {
          options.networking.stevenBlackHosts = {
            enable = mkEnableOption "Steven Black's hosts file";
            enableIPv6 = mkEnableOption "IPv6 rules" // {
              default = config.networking.enableIPv6;
              defaultText = literalExpression "config.networking.enableIPv6";
            };
            blockFakenews = mkEnableOption "fakenews hosts entries";
            blockGambling = mkEnableOption "gambling hosts entries";
            blockPorn = mkEnableOption "porn hosts entries";
            blockSocial = mkEnableOption "social hosts entries";
          };
          config = mkIf cfg.enable {
            networking.extraHosts = filtered;
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
