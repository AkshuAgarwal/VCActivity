"""
MIT License

Copyright (c) 2021 AkshuAgarwal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import traceback
from typing import Union, Optional, TypedDict

from discord import Client, AutoShardedClient, VoiceChannel
from discord.http import Route
from discord.ext.commands import Bot, AutoShardedBot, BotMissingPermissions

from .errors import (
    VCActivityException,
    APIException,
    InvalidChannel,
    InvalidApplicationID
)

all = ('VCApplication', 'VCActivity', )


class VCApplication:
    """Available Voice Channel Target Application IDs."""

    betrayal = 773336526917861400
    chess = 832012586023256104
    fishing = 814288819477020702
    poker = 755827207812677713
    youtube = 755600276941176913

class VCActivity:
    """Represents VCActivity Connection class.
    This class is used to interact with Discord API to create Voice 
    Channel Invite Links to use Discord's Beta VC Activities features.
    
    Parameters
    -----------
    bot: Union[:class:`.Client`, :class:`.AutoShardedClient`, :class:`.Bot`, :class:`.AutoShardedBot`]
        The Main Bot class of the Bot.

    Raises
    -------
    :exc:`TypeError`
        Invalid class type passed in bot parameter.
    """

    def __init__(
        self,
        bot: Union[Client, AutoShardedClient, Bot, AutoShardedBot]
    ):
        if isinstance(bot, (Client, AutoShardedClient, Bot, AutoShardedBot)):
            self.bot = bot
        else:
            raise TypeError(
                'Invalid Client/Bot object parameter passed. '
                'Should be discord.Client/AutoShardedClient/Bot/AutoShardedBot type')

        self._applications: dict = {
            'betrayal': VCApplication.betrayal,
            'chess': VCApplication.chess,
            'fishing': VCApplication.fishing,
            'poker': VCApplication.poker,
            'youtube': VCApplication.youtube,
        }


    async def get_link(
        self,
        voice_channel: Union[VoiceChannel, int],
        application: Union[str, int],
        *,
        max_age: Optional[int] = 86400,
        max_uses: Optional[int] = 0,
        ) -> str:
        """|coro|
        
        Retrieves a Invite Link with VC Activities for the VoiceChannel passed.
        
        Parameters
        -----------
        voice_channel: Union[:class:`int`, :class:`.VoiceChannel`]
            The Voice Channel to create VC Activity Invite Link for.
        application: Union[:class:`str`, :class:`int`]
            The Activity Type to create Invite Link for.
        max_age: Optional[:class:`int`]
            How long the invite should last in seconds. If it’s 0 then the invite doesn’t expire. Should be between 0 to 604800 seconds (7 days). Defaults to 86400 (24 Hours).
        max_uses: Optional[:class:`int`]
            How many uses the invite could be used for. If it’s 0 then there are unlimited uses. Should be between 0 to 100. Defaults to 0.
            
        Raises
        -------
        :exc:`TypeError`
            Invalid class type passed in voice_channel or application.
        :exc:`ValueError`
            Any Value passed is Invalid/Not Acceptable.
        :exc:`.InvalidChannel`
            Voice Channel passed is Invalid.
        :exc:`.BotMissingPermissions`
            Bot is missing permissions to create invites.
        :exc:`.InvalidApplicationID`
            Application ID passed is Invalid.
        :exc:`.APIException`
            API is overloaded while creating Invite.
        :exc:`.VCActivityException`
            Creating Invite link falied.
            
        Returns
        --------
        :class:`str`
            The Invite Link Created."""

        if isinstance(voice_channel, VoiceChannel):
            _vc_id = voice_channel.id
        elif isinstance(voice_channel, int):
            _vc_id = voice_channel
        else:
            raise TypeError(
                'voice_channel parameter must be integer or' 
                f'discord.VoiceChannel type and not "{type(voice_channel).__name__}"'
            )

        if isinstance(application, str):
            if application.lower().replace(' ', '') in self._applications:
                _app_id: int = self._applications[
                    application.lower().replace(' ', '')]

            else:
                raise ValueError('Invalid application type passed. '
                    f'Should be one from {"/".join(i for i in self._applications.keys())}.')

        elif isinstance(application, int):
            _app_id: int = application

        else:
            raise TypeError(
                'application parameter must be string or integer '
                f'and not "{type(application).__name__}"')


        if max_uses < 0 or max_uses > 100:
            raise ValueError(
                'max_uses is limited in the range 0 to 100. '
                'Choose between the given range.')

        if max_age < 0 or max_age > 604800:
            raise ValueError(
                'max_age is limited in the range 0 to 604800 seconds. '
                'Choose between the given range.')


        data = {
            'max_age': max_age,
            'max_uses': max_uses,
            'target_application_id': str(_app_id),
            'target_type': 2,
            'temporary': False,
            'validate': None
        }

        try:
            response = await self.bot.http.request(
                Route('POST', f'/channels/{_vc_id}/invites'), json=data
            )

        except Exception as e:
            if '10003' in str(e):
                raise InvalidChannel('Invalid Channel/ID passed.')
            elif '50013' in str(e):
                raise BotMissingPermissions(['create_instant_invite'])
            elif 'target_application_id' in str(e):
                raise InvalidApplicationID(f'Invalid Application ID ({_app_id}) passed.')
            elif '130000' in str(e):
                raise APIException(
                    'API resource is currently overloaded. '
                    'Try again a little later.')
            else:
                traceback.print_exc()
                raise VCActivityException(
                    'Some Exception occured while creating invite.\n'
                    f'Exception: {e}'
                )

        return f'https://discord.com/invite/{response["code"]}'