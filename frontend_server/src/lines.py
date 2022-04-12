from typing import List


class LinesRepo:
    def __init__(self):
        self.__available_languages = ['en', 'ru']
        self.__user_languages = {}
        self.__lines = {
            "help_create_team": {"en": "to add team", "ru": "чтобы добавить команду"},
            "help_invite_member": {"en": "to invite user", "ru": "чтобы пригласить пользователя"},
            "help_create_meeting": {"en": "to create meeting", "ru": "чтобы создать встречу"},
            "help_invite_to_meeting": {"en": "to invite to meeting", "ru": "чтобы пригласить на встречу"},
            "help_add_daughter_team": {"en": "to add daughter team", "ru": "чтобы добавить дочернюю команду"},
            "help_edit_policy": {"en": "to edit team policy", "ru": "чтобы редактировать политику команды"},
            "help_add_to_meeting": {"en": "to add to meeting", "ru": "чтобы добавить на встречу"},
            "help_update_meeting_time": {"en": "to update meeting time", "ru": "чтобы обновить время встречи"},
            "help_get_agenda": {"en": "to get your agenda", "ru": "чтобы получить расписание"},
            "help_upload_file": {"en": "to upload file", "ru": "чтобы загрузить файл"},
            "help_get_files": {"en": "to get available files", "ru": "чтобы получить доступные файлы"},
            "help_auth_gcal": {"en": "to auth using google calendar",
                               "ru": "чтобы авторизоваться используя гугл календарь"},
            "help_change_language": {"en": "to change language", "ru": "чтобы сменить язык"},
            "help_help": {"en": "to see this message", "ru": "чтобы увидеть это сообщение"},
            "create_team_team_created": {"en": "team created", "ru": "команда создана"},
            "create_team_enter_name": {"en": "Enter name", "ru": "Введите Имя"},
            "invite_user_tag_users": {"en": "Tag one or multiple users",
                                      "ru": "Тэгните одного или нескольких пользователей"},
            "invite_user_invitations_send": {"en": "Invitations were send", "ru": "Приглашения были отправлены"},
            "invite_user_you_were_invited": {"en": "You were invited to team", "ru": "Вы были приглашены в команду"},
            "invite_user_by": {"en": "by", "ru": "от"},
            "invite_user_accept": {"en": "accept", "ru": "принять"},
            "invite_user_reject": {"en": "reject", "ru": "отклонить"},
            "invite_reaction_accepted": {"en": "Accepted", "ru": "Принято"},
            "invite_reaction_rejected": {"en": "Rejected", "ru": "Отклонено"},
            "invite_reaction_accepted_invitation": {"en": "accepted your invitation", "ru": "принял ваше приглашение"},
            "invite_reaction_rejected_invitation": {"en": "rejected your invitation",
                                                    "ru": "отклонил ваше приглашение"},
            "create_meeting_enter_description": {"en": "Enter description", "ru": "Введите описание"},
            "create_meeting_enter_datetime": {"en": "Enter datetime (in format DD-MM-YYYY HH:MM)",
                                              "ru": "Введите дату и время (в формате ДД-ММ-ГГГГ ЧЧ:ММ)"},
            "create_meeting_meeting_created": {"en": "Meeting created", "ru": "Встреча создана"},
            "create_meeting_wait_approval": {"en": "Meeting will be approved by the group owner. Just relax and wait",
                                             "ru": "Встреча будет одобрена владельцем команды. Просто расслабьтесь и ждите"},
            "create_meeting_user": {"en": "User", "ru": "Пользователь"},
            "create_meeting_created_meeting": {"en": "created meeting", "ru": "создал встречу"},
            "create_meeting_approve": {"en": "approve", "ru": "одобрить"},
            "create_meeting_reject": {"en": "reject", "ru": "отклонить"},
            "meeting_approve_approved": {"en": "Approved", "ru": "Одобрено"},
            "meeting_approve_rejected": {"en": "Rejected", "ru": "Отклонено"},
            "meeting_approve_meeting": {"en": "Meeting", "ru": "Встреча"},
            "meeting_approve_was_approved": {"en": "was approved", "ru": "была одобрена"},
            "meeting_approve_was_rejected": {"en": "was rejected", "ru": "была отклонена"},
            "upload_file_send_file": {"en": "send some file", "ru": "отправьте какой-нибудь файл"},
            "upload_file_uploaded": {"en": "Uploaded", "ru": "Загружено"},
            "gcal_auth_open": {"en": "open", "ru": "откройте"},
            "gcal_auth_respond_code": {"en": "and respond with code", "ru": "и ответьте кодом"},
            "gcal_auth_authenticated": {"en": "Authenticated", "ru": "Авторизированы"},
            "gcal_auth_went_wrong": {"en": "Something went wrong. Try again later",
                                     "ru": "Что-то пошло не так. Попробуйте еще раз позже"},
            "get_agenda_today": {"en": "today", "ru": "сегодня"},
            "get_agenda_tomorrow": {"en": "tomorrow", "ru": "завтра"},
            "get_agenda_at": {"en": "at", "ru": "в"},
            "update_meeting_time_enter_datetime": {"en": "Enter datetime (in format DD-MM-YYYY HH:MM)",
                                                   "ru": "Введите дату и время (в формате ДД-ММ-ГГГГ ЧЧ:ММ)"},
            "update_meeting_time_time_updated": {"en": "meeting time was updated to",
                                                 "ru": "время встречи было обновлено на"},
            "add_to_meeting_tag": {"en": "Tag one or multiple users",
                                   "ru": "Тэгните одного или нескольких пользователей"},
            "add_to_meeting_you_were_added": {"en": "You were added to meeting", "ru": "Вы были добавлены на встречу"},
            "add_to_meeting_meeting_starts_at": {"en": "meeting starts at", "ru": "встреча начинается в"},
            "add_to_meeting_users_were_added": {"en": "Users were added to meeting",
                                                "ru": "Пользователи были добавлены на встречу"},
            "inviting_to_meeting_tag": {"en": "Tag one or multiple users",
                                        "ru": "Тэгните одного или нескольких юзеров"},
            "inviting_to_meeting_invitations_send": {"en": "Invitations to meeting were send",
                                                     "ru": "Приглашения на встречу были отправлены"},
            "inviting_to_meeting_you_were_invited": {"en": "You were invited to meeting",
                                                     "ru": "Вы были приглашены на встречу"},
            "inviting_to_meeting_by": {"en": "by", "ru": "от"},
            "inviting_to_meeting_accept": {"en": "accept", "ru": "принять"},
            "inviting_to_meeting_reject": {"en": "reject", "ru": "отклонить"},
            "meeting_invite_reaction_you_accepted": {"en": "You accepted meeting invitation",
                                                     "ru": "Вы приняли приглашение на встречу"},
            "meeting_invite_reaction_you_rejected": {"en": "You rejected meeting invitation",
                                                     "ru": "Вы отклонили приглашение на встречу"},
            "meeting_invite_reaction_meeting_starts_at": {"en": "meeting starts at", "ru": "встреча начинается в"},
            "meeting_invite_reaction_accepted": {"en": "accepted meeting invitation",
                                                 "ru": "принял приглашение на встречу"},
            "meeting_invite_reaction_rejected": {"en": "rejected meeting invitation",
                                                 "ru": "отклонил приглашение на встречу"},
            "add_daughter_team_add_to": {"en": "add daughter team to", "ru": "добавить дочернуюю команду к"},
            "add_daughter_team_enter_id": {"en": "Enter daughter team id", "ru": "Введите айди дочерней команды"},
            "add_daughter_team_is_daughter": {"en": "team is now a daughter of team",
                                              "ru": "команда теперь дочь команды"},
            "edit_policy_edit_of": {"en": "edit policy of team", "ru": "редактировать политику команды"},
            "edit_policy_policy_updated": {"en": "Policy updated", "ru": "Политика обновлена"},
            "edit_policy_enter_one_zero": {"en": "Enter 1 or 0 separated with spaces for each policy parameter",
                                           "ru": "Введите 1 или 0, разделенные пробелами, для каждого параметра политики"},
            "edit_policy_allow_meetings": {"en": "allow users to create meetings",
                                           "ru": "разрешать пользователям создавать встречи"},
            "edit_policy_need_approve": {"en": "need approve for meeting creation",
                                         "ru": "требуется одобрение создания встречи"},
            "edit_policy_propagate_policy": {"en": "propagate policy", "ru": "политика применяется"},
            "edit_policy_parent_visible": {"en": "parent visible", "ru": "родитель видим"},
            "edit_policy_propagate_admin": {"en": "propagate admin", "ru": "админство применяется"},
            "en": {"en": "English", "ru": "Английский"},
            "ru": {"en": "Russian", "ru": "Русский"},
            "change_language_changed": {"en": "Language changed", "ru": "Язык сменен"},
        }

    def get_user_language(self, _user_id: int) -> str:
        if _user_id in self.__user_languages:
            return self.__user_languages[_user_id]
        self.update_user_language(_user_id, 'en')
        return self.get_user_language(_user_id)

    def update_user_language(self, _user_id: int, _language: str) -> str:
        if _language in self.__available_languages:
            self.__user_languages[_user_id] = _language
        return self.get_user_language(_user_id)

    def get_all_languages(self) -> List[str]:
        return self.__available_languages

    def get_line(self, _name: str, _user_id: int) -> str:
        user_language = self.get_user_language(_user_id)
        for _ in self.__lines:
            if _name in self.__lines:
                translations = self.__lines[_name]
                if user_language in translations:
                    return translations[user_language]
