function myTimer() {
    let ticks = parseInt(document.getElementById("timer").innerHTML);

    document.getElementById("timer_vis").style.color = "red";

   if (ticks > 0) {
        ticks = ticks - 1;
        document.getElementById("timer").innerHTML = ticks.toString();

        let t_vis = '';
       if (ticks <= 60) {
           t_vis = ticks.toString();
       }
       else if (ticks < 3600) {
           t_vis = (Math.floor(ticks / 60) + ' : ' + ticks % 60).toString().padStart(2, '0');
       //    if (ticks <= 3600)
       //        document.getElementById("timer_vis").innerHTML = Math.floor((ticks / 60) % 60).toString() + ' : ' +
       //            Math.floor(ticks % 60).toString().padStart(2, '0')
       }
 /*           document.getElementById("timer_vis").innerHTML = Math.floor(ticks % 60).toString()*/
       else {
           t_vis = Math.floor(ticks / 3600).toString().padStart(2, '0') + ' : ' + Math.floor((ticks / 60) % 60).toString().padStart(2, '0') + ' : ' + (ticks % 60).toString().padStart(2, '0');
        //   t_vis = Math.floor((ticks / 3600) % 24).toString().padStart(2, '0') + ' : ' +
        //            Math.floor((ticks / 60) % 60).toString().padStart(2, '0') + ' : ' + Math.floor(ticks % 60).toString().padStart(2, '0')
        }
    document.getElementById("timer_vis").innerHTML = t_vis;
    }
    else {
        // Timer Over
        fetch('/anketa/finish', {
            method: 'POST'
        }).then(() => {
            window.location.href = '/anketa/result_anketa';  // или другой URL на экран итогов
        }).catch(error => console.error('Mistake finish:', error));
    }
    }
setInterval(myTimer, 1000);