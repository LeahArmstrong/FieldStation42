(function (root, factory) {
    const helpers = factory();
    if (typeof module === 'object' && module.exports) {
        module.exports = helpers;
    }
    root.fs42Guide = helpers;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    function pad(value) {
        return String(value).padStart(2, '0');
    }

    function spacePad(value) {
        return String(value).padStart(2, ' ');
    }

    function formatTime(date, format) {
        const hour24 = date.getHours();
        const hour12 = hour24 % 12 || 12;
        const replacements = {
            '%H': pad(hour24), '%-H': String(hour24), '%_H': spacePad(hour24),
            '%I': pad(hour12), '%-I': String(hour12), '%_I': spacePad(hour12),
            '%k': spacePad(hour24), '%-k': String(hour24), '%_k': spacePad(hour24),
            '%l': spacePad(hour12), '%-l': String(hour12), '%_l': spacePad(hour12),
            '%M': pad(date.getMinutes()), '%-M': String(date.getMinutes()), '%_M': spacePad(date.getMinutes()),
            '%S': pad(date.getSeconds()), '%-S': String(date.getSeconds()), '%_S': spacePad(date.getSeconds()),
            '%p': hour24 < 12 ? 'AM' : 'PM',
            '%P': hour24 < 12 ? 'am' : 'pm',
            '%R': `${pad(hour24)}:${pad(date.getMinutes())}`,
            '%T': `${pad(hour24)}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`,
            '%r': `${pad(hour12)}:${pad(date.getMinutes())}:${pad(date.getSeconds())} ${hour24 < 12 ? 'AM' : 'PM'}`,
            '%%': '%'
        };
        const requested = (typeof format === 'string' && format) ? format : '%H:%M';
        return requested.replace(/%%|%[-_]?[HIMSk]|%[-_]?l|%[pPRTr]/g, token => replacements[token] ?? token);
    }

    function programTitles(block) {
        block = block || {};
        const legacyTitle = String(block.title || '').trim();
        const showTitle = String(block.show_title || '').trim();
        let episodeTitle = String(block.episode_title || '').trim();
        const primary = showTitle || legacyTitle || 'Untitled';

        if (episodeTitle && episodeTitle.toLocaleLowerCase() === primary.toLocaleLowerCase()) {
            episodeTitle = '';
        }
        return { primary, secondary: episodeTitle };
    }

    return { formatTime, programTitles };
}));
