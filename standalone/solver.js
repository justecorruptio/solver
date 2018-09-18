PRIME_MAP = {};
[
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41,
    43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101
].map((p, i) => {
    PRIME_MAP[String.fromCharCode(65 + i)] = p;
});

$ = id => document.getElementById(id);
min = (a, b) => a < b ? a : b;
max = (a, b) => a > b ? a : b;
range = (l, h) => Array.from({length: h - l}, (x, i) => l + i);
comb = (pool, r) => {
    var i, j;
    var n = pool.length;
    if(r > n) return [];

    var indices = [];
    for(i = 0; i < r; i++) indices[i] = i;

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

hash = word => {
    var prod = 1;
    for(var letter of word) prod *= PRIME_MAP[letter];
    return prod;
};

snatch = input => {
    var res = {},
        letters = input.filter(word => word.length == 1),
        words = input.filter(word => word.length > 1);

        letter_hashes = range(0, min(letters.length + 1, 15)).map(
            j => comb(letters, j).map(l => [l, hash(l)])
        );

    for(var i = 0; i < min(words.length + 1, 4); i++) {
        comb(words, i).map(w => {
            var c = w.join('');
            if(c.length <= 15) {
                words_hx = hash(c);

                letter_hashes.slice(max(0, 2 - w.length), 15 - c.length).map(entries => {
                    entries.map(([l, letter_hx]) => {
                        var hx = words_hx * letter_hx;
                        if(grams[hx])
                            grams[hx].map(built => {
                                res[[...w.sort(), ...l.sort()].join(' ')] = 1;
                            });
                    });
                });
            }
        });
    }
    return Object.keys(res);
}

formulas = output => {
    var res = [];
    output.map(term => {
        var hx = hash(term.replace(/\W/g, '')),
            equ = term.match(/\w{2,}|\w(?: \w)*/g).join(' + ');
        (grams[hx] || []).map(word => {
            res.push(`${equ} = ${word}`);
        });
    });

    return res.sort((a, b) => a.length > b.length);
};

isWord = word => (
    (grams[hash(word)] || []).indexOf(word) >= 0
)

grams = {};

fetch('owl3.txt').then(resp => resp.text()).then(owl => {
    owl.match(/\w+/g).map(word => {
        var hx = hash(word);
        (grams[hx] = grams[hx] || []).push(word);
    });
});


handleClear = () => {
    $('input').value = '';
    $('answer').innerHTML = '';
}

handleSolve = () => {
    var $answer = $('answer'),
        input = $('input').value.toUpperCase().match(/\w+/g);

    if(!input) return;
    $answer.innerHTML = '';
    if(input.length == 1 && isWord(input[0])) {
        $answer.innerHTML += `<cell class="ok">${input[0]} is a word.</cell>`;
    }
    input.map(word => {
        if(word.length > 1 && !isWord(word)) {
            $answer.innerHTML += `<cell class="err">${word} is not word!</cell>`;
        }
    })

    res = formulas(snatch(input));
    res.map(formula => {
        $answer.innerHTML += `<cell>${formula}</cell>`;
    });
}
