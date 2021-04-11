const NodeAFK = require("afk");

const inactivityDuration = 1000 * 10; // the user will be considered `idle` after 10 seconds

const afk = new NodeAFK(inactivityDuration);

afk.init();

let flag = true;
let second = 00;
let minutes = 00;
let hours = 00;

afk.on("status:idle", () => {
    flag = false;
    console.log("AFK");
});

afk.on("status:active", () => {
    flag = true;
    console.log("back");
});

setInterval(() => {
    if (flag) {
        second = Number(second) + 1;
        second = second < 10 ? `0${second}` : second;
        console.log(`${hours}:${minutes}:${second}`);
        if (second == 59) {
            second = 0;
            minutes = Number(minutes) + 1;
            minutes = minutes < 10 ? `0${minutes}` : minutes;
            if (minutes == 59) {
                minutes = 0;
                hours = Number(hours) + 1;
                hours = hours < 10 ? `0${hours}` : hours;
            }
        }
    }
}, 1000);
