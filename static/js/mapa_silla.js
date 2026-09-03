document.addEventListener('DOMContentLoaded', () => {
    const sala = document.getElementById('sala');
    const numerosInferioresEl = document.getElementById('numeros-inferiores');
    const listaAsientosEl = document.getElementById('lista-asientos');
    const totalAsientosEl = document.getElementById('total-asientos');
    const btnComprar = document.getElementById('btn-comprar');
    const inputAsientos = document.getElementById('input-asientos');

    let seleccionados = [];
    const filas = ['J', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A'];

    filas.forEach(letra => {
        const filaDiv = document.createElement('div');
        filaDiv.classList.add('fila');

        const letraDiv = document.createElement('div');
        letraDiv.classList.add('letra-fila');
        letraDiv.textContent = letra;
        filaDiv.appendChild(letraDiv);

        let zona = 'estandar';
        if (['J', 'I'].includes(letra)) zona = 'vip';
        if (['B', 'A'].includes(letra)) zona = 'preferencial';

        const tieneLaterales = ['C','D','E','F','G','H'].includes(letra);
        
        if (tieneLaterales) {
            filaDiv.appendChild(crearBloque(1, 3, letra, zona));
        } else {
            const espacio = document.createElement('div');
            espacio.classList.add('espacio-lateral');
            filaDiv.appendChild(espacio);
        }

        filaDiv.appendChild(crearBloque(4, 15, letra, zona));

        if (tieneLaterales) {
            filaDiv.appendChild(crearBloque(16, 18, letra, zona));
        }

        sala.appendChild(filaDiv);
    });

    function crearBloque(inicio, fin, letra, claseZona) {
        const bloque = document.createElement('div');
        bloque.classList.add('bloque');

        for (let i = inicio; i <= fin; i++) {
            const asiento = document.createElement('div');
            asiento.classList.add('asiento', claseZona);
            asiento.dataset.codigo = `${letra}${i}`;

            asiento.addEventListener('click', () => {
                asiento.classList.toggle('seleccionado');
                const codigo = asiento.dataset.codigo;

                if (asiento.classList.contains('seleccionado')) {
                    seleccionados.push(codigo);
                } else {
                    seleccionados = seleccionados.filter(item => item !== codigo);
                }
                actualizarResumen();
            });

            bloque.appendChild(asiento);
        }
        return bloque;
    }

    function generarNumerosInferiores() {
        for (let i = 1; i <= 3; i++) crearNumCol(i);
        crearEspacioNum();
        for (let i = 4; i <= 15; i++) crearNumCol(i);
        crearEspacioNum();
        for (let i = 16; i <= 18; i++) crearNumCol(i);
    }

    function crearNumCol(num) {
        const numDiv = document.createElement('div');
        numDiv.classList.add('numero-columna');
        numDiv.textContent = num;
        numerosInferioresEl.appendChild(numDiv);
    }

    function crearEspacioNum() {
        const espacio = document.createElement('div');
        espacio.style.width = '8px';
        numerosInferioresEl.appendChild(espacio);
    }

    function actualizarResumen() {
        listaAsientosEl.textContent = seleccionados.length > 0 ? seleccionados.join(', ') : 'Ninguno';
        totalAsientosEl.textContent = seleccionados.length;
        
        if (inputAsientos) {
            inputAsientos.value = seleccionados.join(',');
        }

        btnComprar.disabled = seleccionados.length === 0;
    }

    generarNumerosInferiores();
});