const mineflayer = require('mineflayer');
const { WebSocketServer } = require('ws');

// --- Bot Setup ---
// NOTE: This bot will require a Minecraft server that is running in "offline mode"
// (online-mode=false in server.properties) because we are not authenticating with Mojang.
const bot = mineflayer.createBot({
    host: 'localhost', // Replace with your server's IP if not running locally
    port: 25565,       // Default Minecraft server port
    username: 'MayaBot'
});

bot.on('login', () => {
    console.log('🤖 MayaBot has logged into the Minecraft server.');
});

bot.on('chat', (username, message) => {
    // Ignore self
    if (username === bot.username) return;
    console.log(`[Minecraft Chat] ${username}: ${message}`);
});

bot.on('error', err => console.error('Bot Error:', err));
bot.on('kicked', reason => console.log('Kicked from server:', reason));

// --- WebSocket Bridge Setup ---
const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', ws => {
    console.log('🐍 Python client connected to WebSocket bridge.');

    // Send world data to Python periodically
    const worldStateInterval = setInterval(() => {
        if (ws.readyState === ws.OPEN) {
            const state = {
                type: 'world_state',
                position: bot.entity.position,
                velocity: bot.entity.velocity,
                onGround: bot.entity.onGround,
                health: bot.health,
                food: bot.food,
                inventory: bot.inventory.items().map(item => ({
                    name: item.name,
                    count: item.count
                }))
            };
            ws.send(JSON.stringify(state));
        }
    }, 2000); // Send state every 2 seconds

    // Listen for commands from Python
    ws.on('message', message => {
        try {
            const command = JSON.parse(message);
            console.log('Received command from Python:', command);

            handleCommand(command);
        } catch (e) {
            console.error('Error processing command from Python:', e);
        }
    });

    ws.on('close', () => {
        console.log('🐍 Python client disconnected.');
        clearInterval(worldStateInterval);
    });
});

function handleCommand(command) {
    const { action, direction, message } = command;

    switch (action) {
        case 'move':
            bot.setControlState(direction, true);
            // Release the key after a short time to simulate a single step
            setTimeout(() => bot.setControlState(direction, false), 200);
            break;
        case 'jump':
            bot.setControlState('jump', true);
            bot.setControlState('jump', false);
            break;
        case 'attack':
            const entity = bot.nearestEntity();
            if (entity) {
                bot.attack(entity);
            }
            break;
        case 'chat':
            bot.chat(message);
            break;
        // Add more complex actions here in the future
    }
}

console.log('🟢 WebSocket bridge server started on port 8080.');
console.log('Waiting for Python client to connect...');