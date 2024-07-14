import {randomUUID, select} from "./resolver.js";
import {readFile} from "fs/promises";


// README
const query = /*first args - string*/ process.argv[2] /*first args - string*/;
const path = /*second arg - string*/ process.argv[3] /*second arg - string*/;

const file = await readFile(path, 'utf-8');
const response = await select(
    query,
    JSON.parse(file)
)

console.log(response);