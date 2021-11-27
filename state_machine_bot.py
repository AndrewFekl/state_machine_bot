from transitions import Machine, State
import telebot


class UserMachine(object):
    """Класс, предназначенный для создания экземпляра State Machine для каждого пользователя"""

    # Список состояний, одинаковый для всех экземпляров класса
    states = ['start', 'pizza_size_choice', 'payment_method_choice', 'order_confirmation']

    def __init__(self):
        # Определим словарь для записи размеров пиццы и способа оплаты отдельного покупателя
        self.users_order = {}

        # Создадим модель машины, в качестве модели используем текущий экземпляр класса
        self.machine = Machine(model=self, states=UserMachine.states, send_event=True, queued=True, initial='start')

        # Добавим необходимые переходы
        # Начало оформления заказа
        self.machine.add_transition('start_order', 'start', 'pizza_size_choice')

        # Этап выбора размера пиццы
        self.machine.add_transition('choice_pizza_size', 'pizza_size_choice', 'payment_method_choice', after='add_size')

        # Этап выбора способа оплаты
        self.machine.add_transition('choice_payment_method', 'payment_method_choice', 'order_confirmation',
                                    after='add_method')
        # Подтверждение заказа
        self.machine.add_transition('order_confirmation', 'order_confirmation', 'start')

    def add_size(self, event):
        self.users_order['size'] = event.kwargs.get('size', 'большую')

    def add_method(self, event):
        self.users_order['method'] = event.kwargs.get('method', 'наличными')

    def get_order_information(self, event):
        size = self.users_order['size']
        method = self.users_order['method']
        information = f'Вы хотите {size} пиццу. Оплата {method}?'
        return information


class TelegramBot(object):
    """Класс, описывающий телеграм-бота и позволяющий его инициализировать"""

    def __init__(self):
        self.users_machines = {}

        TOKEN = "2108034814:AAGS2yJGTZ3TYmnLUPgKOZxmpRuaaD28IBo"
        self.bot = telebot.TeleBot(TOKEN, parse_mode=None)

        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.bot.send_message(message.chat.id,
                                  "Привет! Это пицца бот. Введите что нибудь для начала оформления заказа")
            self.users_machines[message.chat.id] = UserMachine()

        @self.bot.message_handler(func=lambda message: self.get_state(message) == 'start')
        def start_order(message):
            machine = self.users_machines[message.chat.id]
            machine.start_order()
            self.users_machines[message.chat.id] = machine
            self.bot.send_message(message.chat.id, "Какую пиццу вы хотите? Большую или маленькую?")

        @self.bot.message_handler(func=lambda message: self.get_state(message) == 'pizza_size_choice')
        def choose_pizza_size(message):
            machine = self.users_machines[message.chat.id]
            size = message.text
            machine.choice_pizza_size(size=size)
            self.users_machines[message.chat.id] = machine
            self.bot.send_message(message.chat.id, "Как вы будете платить?")

        @self.bot.message_handler(func=lambda message: self.get_state(message) == 'payment_method_choice')
        def choose_payment_method(message):
            machine = self.users_machines[message.chat.id]
            method = message.text
            machine.choice_payment_method(method=method)
            confirmation_message = machine.get_order_information(None)
            self.users_machines[message.chat.id] = machine
            self.bot.send_message(message.chat.id, confirmation_message)

        @self.bot.message_handler(func=lambda message: self.get_state(message) == 'order_confirmation')
        def order_confirmation(message):
            machine = self.users_machines[message.chat.id]
            confirmation = message.text.lower()
            machine.order_confirmation()
            if 'да' in confirmation:
                self.bot.send_message(message.chat.id, 'Спасибо, ваш заказ принят')
            else:
                self.bot.send_message(message.chat.id, 'Повторите оформление заказа')
            del self.users_machines[message.chat.id]

    def get_state(self, message):
        return self.users_machines[message.chat.id].state

class StateMachineBot():
    """Класс универсального бота на основе стейт-машины. Принимает аргументом при инициализации
    объект чат бота (по умолчанию телеграм) и запускает его работу"""

    def __init__(self, bot=None):
        self.bot = bot or TelegramBot()

        if isinstance(self.bot, TelegramBot):
            self.bot.bot.infinity_polling()

def _main():
    bot = StateMachineBot(TelegramBot())

if __name__ == '__main__':
    _main()












