const mineflayer = require('mineflayer');
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 3000 });

let bot = null;

wss.on('connection', ws => {
  ws.on('message', message => {
    const data = JSON.parse(message);
    const { command, args } = data;

    if (command === 'connect') {
      bot = mineflayer.createBot({
        host: args.host || 'localhost',
        port: args.port || 25565,
        username: args.username || 'Maya'
      });

      bot.on('login', () => {
        ws.send(JSON.stringify({ status: 'connected' }));
      });

      bot.on('error', err => {
        ws.send(JSON.stringify({ status: 'error', message: err.message }));
      });

      bot.on('end', () => {
        ws.send(JSON.stringify({ status: 'disconnected' }));
        bot = null;
      });

    } else if (bot) {
      switch (command) {
        case 'disconnect':
          bot.quit();
          break;
        case 'chat':
          bot.chat(args.message);
          ws.send(JSON.stringify({ status: 'message sent' }));
          break;
        case 'move':
          const { x, y, z } = args;
          bot.pathfinder.setGoal(new bot.pathfinder.goals.GoalBlock(x, y, z));
          ws.send(JSON.stringify({ status: 'moving' }));
          break;
        case 'get_world_state':
          const worldState = {
            inventory: bot.inventory.items().map(item => ({ name: item.name, count: item.count })),
            position: bot.entity.position
          };
          ws.send(JSON.stringify(worldState));
          break;
        case 'game_action':
          const { game_command, game_args } = args;
          if (bot[game_command]) {
            bot[game_command](...game_args);
            ws.send(JSON.stringify({ status: 'action executed' }));
          } else {
            ws.send(JSON.stringify({ status: 'unknown game command' }));
          }
          break;
        default:
          ws.send(JSON.stringify({ status: 'unknown command' }));
      }
    } else {
      ws.send(JSON.stringify({ status: 'not connected' }));
    }
  });
});

console.log('Minecraft bot WebSocket server started on port 3000');
