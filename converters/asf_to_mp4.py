import ffmpeg


class ASFtoMP4Converter:
    def __init__(self):
        pass


    def convert(input_path, output_path):
        """
        Converte um arquivo ASF para MP4 usando ffmpeg
        """
        try:
            (
                ffmpeg
                .input(input_path)
                .output(output_path, vcodec='libx264', acodec='aac', strict='experimental')
                .run(overwrite_output=True, quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Erro na conversão: {e.stderr.decode('utf-8')}")
            return False
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            return False