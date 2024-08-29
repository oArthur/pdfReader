from fastapi import FastAPI, HTTPException
import requests
from pdf2image import convert_from_path
import pytesseract
import tempfile
import os

# precisa instalra o tesseract-ocr na maquina
app = FastAPI()

@app.get("/ler-boleto/")
async def ler_boleto(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # cria um arquivo temp para salvar o PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(response.content)
            temp_pdf_path = temp_pdf.name

        pages = convert_from_path(temp_pdf_path)

        tessdata_dir = '/opt/homebrew/share/tessdata'
        #trocar esse diretorio, para local que esta instalado na maquina

        texto_completo = ""
        for page in pages:
            texto_completo += pytesseract.image_to_string(page, lang='por', config=f'--tessdata-dir {tessdata_dir}') + "\n"
            #possibilidade de precisar instalar lang por [ https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata ]
            # colocar no diretorio de instalacao: /.../tessdata
        os.remove(temp_pdf_path)

        return {"texto": texto_completo.strip()}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Erro ao baixar o PDF: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o PDF: {str(e)}")


# run uvicorn main:app --reload --host 0.0.0.0 --port 8000