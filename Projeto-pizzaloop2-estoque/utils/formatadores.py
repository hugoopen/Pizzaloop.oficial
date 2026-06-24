def aplicar_mascara_cpf(evento):
    texto_numerico = ''.join(filter(str.isdigit, evento.widget.get()))
    cpf_formatado = ""
    for indice, caractere in enumerate(texto_numerico):
        if indice == 3 or indice == 6:
            cpf_formatado += "."
        elif indice == 9:
            cpf_formatado += "-"
        cpf_formatado += caractere
    evento.widget.delete(0, "end")
    evento.widget.insert(0, cpf_formatado[:14])


def aplicar_mascara_tel(evento):
    texto_numerico = ''.join(filter(str.isdigit, evento.widget.get()))
    tel_formatado = ""
    for indice, caractere in enumerate(texto_numerico):
        if indice == 0:
            tel_formatado += "("
        elif indice == 2:
            tel_formatado += ") "
        elif indice == 7:
            tel_formatado += "-"
        tel_formatado += caractere
    evento.widget.delete(0, "end")
    evento.widget.insert(0, tel_formatado[:15])


def formatar_cpf(valor_cpf):
    numeros = ''.join(filter(str.isdigit, str(valor_cpf)))
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    return numeros


def formatar_telefone(valor_tel):
    numeros = ''.join(filter(str.isdigit, str(valor_tel)))
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return numeros
