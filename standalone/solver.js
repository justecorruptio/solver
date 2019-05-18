String.prototype.sort = function() { return this.split('').sort(); };

$ = id => document.getElementById(id);
max = (a, b) => a > b ? a : b;
range = (l, h) => Array.from({length: h - l}, (x, i) => l + i);
comb = (pool, r) => {
    var i, j;
    var n = pool.length;
    if(r > n) return [];

    var indices = range(0, r);
    var ret = [];

    while(1) {
        ret.push(indices.map(i => pool[i]))
        for(i = r - 1; i >= 0; i--)
            if(indices[i] != i + n - r)
                break;
        if(i < 0) break;
        indices[i] += 1
        for(j = i + 1; j < r; j++)
            indices[j] = indices[j - 1] + 1;
    }
    return ret;
}

hash = word => word.sort().join('');

snatch = input => {
    var res = new Set(),
        letters = input.filter(word => word.length == 1),
        words = input.filter(word => word.length > 1),

        letter_combs = range(0, 10).map(
            j => comb(letters, j).map(l => l.join(''))
        );

    range(0, 5).forEach(i => {
        comb(words, i).forEach( w => {
            var c = w.join('');
            if(c.length > 15) return;

            var combs = letter_combs.slice(max(0, 2 - w.length), 16 - c.length);

            combs.forEach(entries => {
                entries.forEach(l => {
                    if(grams[hash(c + l)])
                        res.add([...w.sort(), ...l.sort()].join(' '));
                });
            });
        });
    });
    return res;
}

subtract = (b, a) => {
    for(var letter of a)
        b = b.replace(letter, '');
    return b;
}

extend = word => {
    var additions = new Set(),
        regex = new RegExp(hash(word).split('').join('.*'));

    for(var hx in grams)
        if(hx.match(regex))
            additions.add(hash(subtract(hx, word)));
    return Array.from(additions)
        .map(letters => [word, ...letters.split('')].join(' '));
};

formulas = output => {
    var res = [];
    output.forEach(term => {
        var hx = hash(term.replace(/\W/g, '')),
            equ = term.match(/\w{2,}|\w(?: \w)*/g).join(' + ');
        (grams[hx] || []).forEach(word => {
            res.push(`${equ} = ${word}`);
        });
    });
    return res.sort((a, b) => a.length - b.length || a > b);
};

isWord = word => (grams[hash(word)] || []).indexOf(word) >= 0

grams = {};

[1,2,3].forEach(i => {
    fetch(`owl2018_0${i}.txt`).then(resp => resp.text()).then(owl => {
        var start_ts = Date.now();
        owl.match(/\w+/g).forEach(word => {
            var hx = hash(word);
            (grams[hx] = grams[hx] || []).push(word);
        });
        $('time').innerText = Date.now() - start_ts;
    });
});

cell = (str, cls) => `<cell class="${cls || ''}">${str}</cell>`;

handleClear = () => {
    $('answer').innerHTML = '';
    $('input').value = '';
    $('input').focus();
}

handleSolve = (checkOnly) => {
    var start_ts = Date.now();
        value = $('input').value.toUpperCase(),
        input = value.match(/\w+/g),
        res = [],
        output = '';

    if(!input) return;

    input.forEach((word, i) => {
        var good = isWord(word);
        if(good && checkOnly)
            output += cell(`${word} is a word.`, 'ok');
        else if(!good && word.length > 1)
            output += cell(`${word} is not word!`, 'err');
    })

    if(!checkOnly) {
        if(input.length > 1)
            res = snatch(input);
        else if(input[0].length > 2)
            res = extend(input[0]);
    }

    output += formulas(res).map(cell).join('');

    $('answer').innerHTML = output || cell('No solution!');
    $('time').innerText = Date.now() - start_ts | 0;
}
