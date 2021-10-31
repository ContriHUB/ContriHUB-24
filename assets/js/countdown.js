const eventBox= document.getElementById('event-box')
const eventDate = Date.parse(eventBox.textContent)
setInterval(()=>{
    const now = new Date().getTime()
    const diff = eventDate - now
    const days = Math.floor( (diff/(1000*60*60*24)) )
    const hours = Math.floor( (diff/(1000*60*60))%24 )
    const minutes = Math.floor((diff/(1000*60))%60 )
    const seconds = Math.floor((diff/1000)%60 )
    if(diff>0){
        document.getElementById("countdown-box").innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s "
    }
    else{
        document.getElementById("countdown-box").innerHTML = " Time Expired For Issue ! "
    }
},1000)
