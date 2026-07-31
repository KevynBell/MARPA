const chat=document.getElementById("chat");
const prompt=document.getElementById("prompt");

async function sendPrompt(){

    const text=prompt.value.trim();

    if(!text){
        return;
    }

    chat.innerHTML+=`<p><span class="user">You:</span> ${text}</p>`;

    prompt.value="";

    const response=await fetch("/chat",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            prompt:text
        })

    });

    const data=await response.json();

    chat.innerHTML+=`<p><span class="marpa">MARPA:</span> ${data.response}</p>`;

    chat.scrollTop=chat.scrollHeight;

}
