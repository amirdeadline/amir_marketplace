#!/usr/bin/env node
'use strict';
const path = require('path');
const { spawnServer } = require('../_lib/spawn_server');
spawnServer(path.resolve(__dirname), 'src/server.py', 'palo-confluence-mcp');
