const inputField = document.getElementById("input");

const utterances = [ 
    ["how are you", "how is life", "how are things"],        //0
    ["hi", "hey", "hello", "good morning", "good afternoon"],      //1
    ["what are you doing", "what is going on", "what is up"],      //2
    ["find data scientist job"],					//3
    ["who are you", "are you human", "are you bot", "are you human or bot"],   //4
    ["can you send me the job detail on my iphone"],//5
    ["recommend some sde job"], //6

]
   
  // Possible responses corresponding to triggers
   
  const answers = [
     [
      "Fine... how are you?",
      "Pretty well, how are you?",
      "Fantastic, how are you?"
    ],         //0                                                                         	//0
    [
      "Hello!", "Hi!", "Hey!", "Hi there!", "Howdy"
    ],						//1
    [
      "Nothing much",
      "About to go to sleep",
      "Can you guess?",
      "I don't know actually"
    ],						//2
    ["There are 3 jobs related to data scientist "],					//3
    ["I am just a bot", "I am a bot. What are you?"],	//4
    ["I have sent all related information to your phone."], //5
    ["There are 3 jobs related to data scientist: 1. data scientist 2. data scientist lead 3.XXX "],//6
    ["There are 3 jobs related to  software delvopement"],
   
  ]
   
  // For any other user input
   
const alternatives = [
    "Go on...",
    "Try again",
    "I will improve in the future by liang."
  ]


inputField.addEventListener("keydown", (e) => {
  if (e.code === "Enter") {
    let input = inputField.value;
    inputField.value = "";
    output(input);
  }
});

function output(input) {
  let product;
  let text = input.toLowerCase().replace(/[^\w\s\d]/gi, "");
  text = text
    .replace(/ a /g, " ")
    .replace(/whats/g, "what is")
    .replace(/please /g, "")
    .replace(/ please/g, "")
    .replace(/r u/g, "are you");

  if (compare(utterances, answers, text)) {
    // Search for exact match in triggers
    product = compare(utterances, answers, text);
  } 
  else {
    product = alternatives[Math.floor(Math.random() * alternatives.length)];
  }

  addChatEntry(input, product);
}

// function compare(utterancesArray, answersArray, string) {
//     let reply;
//     let replyFound = false;
    
//     // Check for partial matches in the triggers
//     for (let x = 0; x < utterancesArray.length; x++) {
//       for (let y = 0; y < utterancesArray[x].length; y++) {
//         if (string.includes(utterancesArray[x][y])) {
//           let replies = answersArray[x];
//           reply = replies[Math.floor(Math.random() * replies.length)];
//           replyFound = true;
//           break;
//         }
//       }
//       if (replyFound) {
//         break;
//       }
//     }
    
//     return reply;
//   }
  function compare(utterancesArray, answersArray, string) {
    let reply;
    let replyFound = false;
    const lowercaseString = string.toLowerCase(); // Convert user input to lowercase for case-insensitive comparison
  
    // Check for partial matches in the triggers
    for (let x = 0; x < utterancesArray.length; x++) {
      for (let y = 0; y < utterancesArray[x].length; y++) {
        const lowercaseUtterance = utterancesArray[x][y].toLowerCase(); // Convert trigger to lowercase for case-insensitive comparison
        if (lowercaseString.includes(lowercaseUtterance)) {
          let replies = answersArray[x];
          reply = replies[Math.floor(Math.random() * replies.length)];
          replyFound = true;
          break;
        }
      }
      if (replyFound) {
        break;
      }
    }
    
    return reply;
  }
  

// function addChatEntry(input, product) {
//   const messagesContainer = document.getElementById("messages");
//   let userDiv = document.createElement("div");
//   userDiv.id = "user";
//   userDiv.className = "user response";
//   userDiv.innerHTML = `<span>${input}</span>`;
//   messagesContainer.appendChild(userDiv);

//   let botDiv = document.createElement("div");
//   let botText = document.createElement("span");
//   botDiv.id = "bot";
//   botDiv.className = "bot response";
//   botText.innerText = "Typing...";
//   botDiv.appendChild(botText);
//   messagesContainer.appendChild(botDiv);

//   messagesContainer.scrollTop =
//     messagesContainer.scrollHeight - messagesContainer.clientHeight;

//   setTimeout(() => {
//     botText.innerText = `${product}`;
//   }, 2000);
// }
// function addChatEntry(input, product) {
//     const messagesContainer = document.getElementById("messages");
//     let userDiv = document.createElement("div");
//     userDiv.id = "user";
//     userDiv.className = "user response";
//     userDiv.innerHTML = `<span>${input}</span>`;
//     messagesContainer.appendChild(userDiv);
  
//     let botDiv = document.createElement("div");
//     let botText = document.createElement("span");
//     botDiv.id = "bot";
//     botDiv.className = "bot response";
  
//     // Use the 'textContent' property instead of 'innerText'
//     botText.textContent = `${product}`;
//     botDiv.appendChild(botText);
//     messagesContainer.appendChild(botDiv);
  
//     // Scroll to the bottom of the chat window
//     messagesContainer.scrollTop = messagesContainer.scrollHeight;
//   }
  
  function addChatEntry(input, product) {
    const messagesContainer = document.getElementById("messages");
    let userDiv = document.createElement("div");
    userDiv.id = "user";
    userDiv.className = "user response";
    userDiv.innerHTML = `<span>${input}</span>`;
    messagesContainer.appendChild(userDiv);
  
    let botDiv = document.createElement("div");
    let botText = document.createElement("span");
    botDiv.id = "bot";
    botDiv.className = "bot response";
  
    // Split long responses into smaller chunks
    const chunkSize = 100; // Adjust the chunk size as needed
    const chunks = product.match(new RegExp(`.{1,${chunkSize}}`, "g")) || [];
  
    let currentChunk = 0;
  
    function displayNextChunk() {
      if (currentChunk < chunks.length) {
        botText.textContent = chunks[currentChunk];
        currentChunk++;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        setTimeout(displayNextChunk, 1000); // Delay between chunks (adjust as needed)
      }
    }
  
    displayNextChunk();
  
    botDiv.appendChild(botText);
    messagesContainer.appendChild(botDiv);
  }
  