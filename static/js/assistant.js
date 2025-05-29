class CyberAssistant {
    constructor() {
      this.voice = new webkitSpeechRecognition();
      this.voice.continuous = true;
      
      this.voice.onresult = (event) => {
        const transcript = event.results[event.results.length-1][0].transcript;
        this.processCommand(transcript);
      }
    }
  
    processCommand(command) {
      const actions = {
        'yeni yazı ekle': () => window.location = '/admin/blogpost/add/',
        'karanlık tema': () => document.body.classList.add('dark-mode'),
        'arama yap': (query) => this.search(query)
      };
      
      Object.entries(actions).forEach(([key, action]) => {
        if(command.toLowerCase().includes(key)) {
          action(command.replace(key, '').trim());
        }
      });
    }
  }
  
  new CyberAssistant().voice.start();