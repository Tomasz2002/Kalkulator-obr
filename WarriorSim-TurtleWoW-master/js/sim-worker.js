importScripts(
    './data/levelstats.min.js',
    './data/gear_turtle.min.js',
    './data/enchants_turtle.min.js',
    './classes/player.min.js',
    './classes/simulation.min.js',
    './classes/spell.min.js',
    './classes/weapon.min.js',
    './globals.min.js',
);

onmessage = (event) => {
    const params = event.data;
    if (params.globals.turtle) {
        importScripts('./data/talents_turtle.min.js');
        importScripts('./data/spells_turtle.min.js');
        importScripts('./data/buffs_turtle.min.js');
    } else {
        importScripts('./data/talents.min.js');
        importScripts('./data/spells.min.js');
        importScripts('./data/buffs.min.js');
    }
    updateGlobals(params.globals);
    const player = new Player(...params.player);
    const sim = new Simulation(player, (report) => {
        // Finished
        if (params.fullReport) {
            report.player = player.serializeStats();
            report.spread = sim.spread;
        }
        postMessage([TYPE.FINISHED, report]);
    }, (iteration, report) => {
        // Update
        postMessage([TYPE.UPDATE, iteration, report]);
    }, params.sim);
    sim.startSync();
};

