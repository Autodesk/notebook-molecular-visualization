# Copyright 2016 Autodesk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import threading
from uuid import uuid4

import ipywidgets as widgets
import traitlets
from nbmolviz.utils import Measure


def _identity(x): return x

class MessageWidget(widgets.DOMWidget):
    """A widget to send messages back and forth between the
    javascript and python interpreters"""
    viewerId = traitlets.Unicode(sync=True)
    _width = traitlets.Unicode(sync=True)
    _height = traitlets.Unicode(sync=True)
    _convert_units = _identity

    def __init__(self, width=500, height=350, **kwargs):
        super(MessageWidget, self).__init__(width=width, height=height, **kwargs)
        self.viewer_ready = False
        self.js_events = {}
        self.message_queue = []
        self.js_event_handlers = {'ready':self._handle_viewer_ready,
                                  'function_done':self._handle_function_done}
        self.messages_received = []
        self._width = str(Measure(width))
        self._height = str(Measure(height))
        self.sent_messages = []
        self.num_calls = 0
        self.viewerId = 'molviz'+str(uuid4())
        self.js_results = {}
        self.on_msg(self._handle_js_message)
        self._batched = []

    def viewer(self, function_name, args, block=False):
        """
        TODO: make blocking/synchronous comms work
        :param function_name:
        :param args:
        :param block:
        :return:
        """
        call_id = self.num_calls + 1
        message = {'event': 'function_call',
                   'function_name': function_name,
                   'arguments': args,
                   'call_id': call_id}

        #Set up an event to wait for this to return
        event = threading.Event()
        self.js_events[call_id] = event
        my_result = {'Warning':'The javascript call to %s has not yet returned. ' % function_name +
                               'This dictionary will be updated when it does.'}
        self.js_results[call_id] = my_result

        #Send the message to javascript
        if self.viewer_ready:
            self.sent_messages.append(message)
            self.send(message)
        else:
            self.message_queue.append(message)
        self.num_calls = call_id

        if block: raise NotImplementedError("blocking doesn't work yet!")
        return my_result

    def batch_message(self, function_name, args):
        self._batched.append((function_name, args))

    def send_batch(self):
        self.viewer('batchCommands', [self._batched])
        self._batched = []

    def _handle_viewer_ready(self,message):
        self.viewer_ready = True
        for message in self.message_queue:
            self.sent_messages.append(message)
            self.send(message)

    def _handle_js_message(self, self_again, content, buffers):
        event = content['event']
        self.messages_received.append(content)
        try:
            handler = self.js_event_handlers[event]
        except KeyError:
            errmsg = ("No handler found for JS event %s\n"%event +
                      "Handlers: %s\n"%str(self.js_event_handlers.keys()) +
                      "Message: %s\n"%content)
            raise KeyError(errmsg)
        else:
            handler(content)

    def _handle_function_done(self,message):
        #Update the user's result dictionary
        call_id = message['call_id']
        if call_id in self.js_results:
            result_dict = self.js_results[call_id]
            result_dict.pop('Warning', None)
            if 'result' in message:
                try:
                    result_dict.update(message['result'])
                except ValueError:
                    result_dict['result'] = message['result']

        #Wake up anyone waiting for the function to return
        if call_id in self.js_events:
            self.js_events[call_id].set()



