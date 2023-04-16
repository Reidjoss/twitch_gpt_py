import socket, time, re
from gpt import gpt


class twitch_BOT():


    def __init__(self, data):
        self.irc_server = data['twitch_bot']['server']
        self.port = data['twitch_bot']['port']
        self.token = data['twitch_bot']['token']
        self.nickname = data['twitch_bot']['nickname']
        self.channel_to_monitor = data['twitch_bot']['channel_to_monitor']
        self.allowed_users = data['twitch_bot']['whitelisted']
        self.gpt_chat = gpt(data)
        self.command_flag = False


    def sock_create(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        
    def connect_to_irc(self):
        try:
            self.s.connect((self.irc_server, int(self.port)))
            self.s.send(f"PASS {self.token}\n".encode('utf-8'))
            self.s.send(f"NICK {self.nickname}\n".encode('utf-8'))
            self.s.send(f"JOIN {self.channel_to_monitor}\n".encode('utf-8'))
            self.s.settimeout(1)
            print(f"Socket stablished with IRC:: {self.channel_to_monitor}")
        except Exception as e:
            print(f"Error stablishing socket with IRC:: {e}")


    def listen_irc(self):
        while True:
            try:
                irc_answer = self.s.recv(1024).decode('utf-8')
                if irc_answer.startswith('PING'):
                    self.s.send("PONG\n".encode('utf-8'))
                else:
                    self.capture_irc_answer(irc_answer)
            except TimeoutError:
                continue
            except Exception as e:
                print(f"Error on listening server: {e}")
                break
            time.sleep(0.1)


    def capture_irc_answer(self, irc_answer):
        if irc_answer == "": raise
        match = irc_answer.find('PRIVMSG')
        if match != -1:
            text_to_capture = f".tmi.twitch.tv PRIVMSG {self.channel_to_monitor} :"
            usr_str, msg_str = irc_answer.split(text_to_capture)
            _, usr = usr_str.split('@')
            msg_str = msg_str[:-2]
            print(f"Message from usr => {usr}: {msg_str}")
            if "!chat" in msg_str.split() and usr in self.allowed_users:
                response = f"@{usr}: "
                try:
                    response += self.gpt_chat.send_request(msg_str.split("!chat")[-1])
                    print(response)
                    success = self.send_chat_message(response)
                except Exception as e:
                    print(f"Error sending prompt to GPT => {e}")
            else:
                pass
        return


    def run(self):
        self.sock_create()
        self.connect_to_irc()
        self.listen_irc()
        

    def send_chat_message(self, message_to_send: str) -> bool:
        try:
            print(f"Sending message => {message_to_send}")
            message_coded = (f"PRIVMSG {self.channel_to_monitor} :{message_to_send}\r\n").encode('utf-8')
            self.s.send(message_coded)
            success = True
        except Exception as e:
            print(f"Error on sending message to server: {e}")
            success = False
        return success


    def set_command_flag(self, state):
        self.command_flag = state