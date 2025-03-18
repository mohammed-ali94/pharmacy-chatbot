{ pkgs }: {
  deps = [
    pkgs.python39Full
    pkgs.python39Packages.pip
  ];
  shellHook = ''
    pip install -r requirements.txt
  '';
}
