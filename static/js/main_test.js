// main.js
import { io } from "https://cdn.socket.io/4.7.2/socket.io.esm.min.js";

const socket = io("http://localhost:5081");
socket.on("connect", () => console.log("✅ Connected"));
