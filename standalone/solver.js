String.prototype.sort = function() { return this.split('').sort(); };

$ = id => document.getElementById(id);
min = (a, b) => a < b ? a : b;
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

    range(0, 4).forEach(i => {
        comb(words, i).forEach( w => {
            var c = w.join('');
            if(c.length > 15) return;

            var combs = letter_combs.slice(max(0, 2 - w.length), 15 - c.length);

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
    var res = new Set(),
        regex = new RegExp(hash(word).split('').join('.*'));

    for(var hx in grams)
        if(hx.match(regex))
            res.add([word, ...subtract(hx, word).sort()].join(' '));
    return res;
}

formulas = output => {
    var res = [];
    output.forEach(term => {
        var hx = hash(term.replace(/\W/g, '')),
            equ = term.match(/\w{2,}|\w(?: \w)*/g).join(' + ');
        (grams[hx] || []).forEach(word => {
            res.push(`${equ} = ${word}`);
        });
    });

    return res.sort((a, b) => a.length > b.length);
};

isWord = word => (grams[hash(word)] || []).indexOf(word) >= 0

grams = {};

fetch('owl3.txt').then(resp => resp.text()).then(owl => {
    var start_ts = Date.now();
    owl.match(/\w+/g).forEach(word => {
        var hx = hash(word);
        (grams[hx] = grams[hx] || []).push(word);
    });
    $('time').innerText = Date.now() - start_ts;
});

handleClear = () => {
    $('answer').innerHTML = '';
    $('input').value = '';
    $('input').focus();
}

handleSolve = () => {
    var start_ts = Date.now();
        value = $('input').value.toUpperCase(),
        input = value.match(/\w+/g),
        is_extend = !!value.match(/\?/),
        res = [],
        output = '';

    if(!input) return;

    if(input.length == 1 && isWord(input[0])) {
        output += `<cell class="ok">${input[0]} is a word.</cell>`;
    }
    input.forEach(word => {
        if(word.length > 1 && !isWord(word)) {
            output += `<cell class="err">${word} is not word!</cell>`;
        }
    })

    if(input.length > 1)
        res = snatch(input);
    else if(input[0].length > 2 && is_extend)
        res = extend(input[0]);

    formulas(res).forEach(formula => {
        output += `<cell>${formula}</cell>`;
    });

    if(!output) {
        output += `<cell>No solution!</cell>`;
    }

    $('answer').innerHTML = output;
    $('time').innerText = Date.now() - start_ts | 0;
}
