String.prototype.sort = function(){return [...this].sort().join('')};
$ = x => document.querySelector(x);
$$ = x => document.querySelectorAll(x);
LETTERS = [...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'];
ALL = {}; GRAMS = {}; DEFS = {}; POS = {}; RANKS = {};

fetchFile = async (fn, cb) => (await (await fetch(fn)).text()).match(/[^\n]+/g).forEach(cb);

Promise.all([
    fetchFile('nwl2023.txt', word => {
        word = word.toUpperCase();
        ALL[word] = true;
        (GRAMS[word.sort()] ||= []).push(word);
    }),
    fetchFile('def.txt', line => {
        let [, words, def, pos] = line.match(/(.+)\t([ A-Z]+([a-z]+).+)/);
        words.toUpperCase().split(' ').forEach(word => {
            (DEFS[word] ||= []).push(def);
            (POS[word] ||= {})[pos] = 1;
        });
    }),
    fetchFile('ranks.txt', line => {
        let [hash, rank] = line.split('\t');
        RANKS[hash] = rank | 0;
    }),
]).then(() => {$('#input').disabled = false})

ulu = (pattern) => {
    let check_len = /@/.test(pattern) ? ()=>true : l => l == pattern.length || null,
        regex = RegExp(['^', ...pattern.replace(/\W/g, '').sort(), '$'].join('.*'));
    return (word) => check_len(word.length) && word.sort().match(regex) && [word];
}

cell = (str, cls, word) => `<cell class="${cls || ''}"
    ${word ? `data-word="${word}" data-hash="${word.sort()}"` : ''}
    onclick="handleClickCell(event)">${str}</cell>`;

annotate = (word) => {
    let sm = (cls, text) => `<small class="annotation ${cls}">${text}</small>`,
        hook = (a, b) => LETTERS.filter(l => ALL[a + l + b]).join(''),
        hidden = $('#checkAnnotate').checked ? '' : 'hidden',
        rank = (RANKS[word.sort()] || 99999) / 20000,
        dot = w => ALL[w] ? '●' : '';
    return `<div class="annotation-container ${hidden}">
        ${sm('left', hook('', word) + dot(word.slice(1)))}
        ${sm('super left', '★'.repeat(rank))} ${word}
        ${sm('right', dot(word.slice(0,-1)) + hook(word, ''))}
        ${sm('super right', Object.keys(POS[word] || {}).join('&nbsp;'))}
    </div>`;
}

handleFind = (type) => {
    var input = $('#input').value = $('#input').value.trim().toUpperCase();
    if (!input) return;
    var isRegexMode = $('#checkRegex').checked,
        [regex, ...clauses] = input.match(/(?<!\?)([^? :][^ :]*)/g),
        wrappedRegex = `^${regex.replace(/@/g,'(.+)')}$`,
        rand=input.match(/(?<=\?)\d+/)|0,
        sortKey = w => type == 'alpha' ? w.sort() : w;
    var res = Object.keys(ALL).map(
        isRegexMode ? word => word.match(wrappedRegex) : ulu(regex)
    ).filter(matches => matches && clauses.every(clause => {
        var [, op, len] = clause.match(/^([<>=])(\d+)$/) || [];
        return op ? eval(`matches[0].length ${op}= ${len}`)
            : ALL[clause.replace(/\d/g, x => matches[x|0])];
    })).map(x => x[0]);
    if (rand) res = res.sort(() => Math.random() - .5).slice(0, rand);
    if (!isRegexMode) res = [...new Set(res.flatMap(w => GRAMS[w.sort()]))];
    res.sort((a, b) => a.length - b.length || (sortKey(a) > sortKey(b) ? 1 : -1));
    $("#count").innerHTML = res.length;
    $('#answer').innerHTML = res.map(
        word => cell(annotate(word), type && `hidden ${type}`, word)
    ).join('') || cell('No solution!');
    $('#input').focus();
};

getCell = (el, cls) => {
    $$('.last-got').forEach(x => x.classList.remove('last-got'));
    el.classList.replace('hidden', cls);
    el.classList.add('last-got');
    $("#count").innerHTML = $$('cell.hidden').length;
}

handleInput = ({keyCode, shiftKey}) => {
    var input = $('#input').value.toUpperCase().trim();
    if (!input || keyCode != 13) return;
    if (shiftKey) return handleFind();
    var el = $(`cell[data-word="${input}"]`);
    if (el) getCell(el, 'got');
    else $('#answer').innerHTML += cell(input, ALL[input]?'err good':'err');
    $('#input').value = '';
};

handleAnnotation = () => $$('.annotation-container').forEach(x => x.classList.toggle('hidden'));
handleReveal = () => $$('cell.hidden').forEach(x => x.classList.replace('hidden', 'missed'));

handleClickCell = ({target, target: {dataset: {word}}}) => {
    if (target.matches('.err')) return target.remove();
    if (target.matches('.hidden')) return getCell(target, 'missed');
    if (!word) return;
    $('#def').innerText = (DEFS[word]||[]).join('\n') || 'No definition';
    $('#def').style.display = 'block';
}

visualViewport.onresize = ({target: {height}}) => $('html').style.setProperty('--vh', height + 'px');
