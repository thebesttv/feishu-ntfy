{ stdenv
, lib
, makeWrapper
, coreutils
, util-linux
, curl
, python3
}:
stdenv.mkDerivation rec {
  pname = "feishu-ntfy";
  version = "0.0.1";

  src = ./.;

  nativeBuildInputs = [ makeWrapper ];

  buildInputs = [
    # coreutils
    # util-linux
    curl
    python3
  ];

  installPhase = ''
    mkdir -p $out/bin
    cp ntfy $out/bin/ntfy

    wrapProgram $out/bin/ntfy \
        --prefix PATH : ${lib.makeBinPath buildInputs}
  '';
}
