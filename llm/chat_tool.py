from config import LLM_ROBOT_ROLE, LLM_USER_ROLE
from database.conversation import update_conversation_time, create_conversation, create_message, get_conversation_dict, get_message_via_cid

def fix_abnormal_chat(st_object):
    if len(st_object.session_state.messages) != 0:  # 如果有历史会话
        if len(st_object.session_state.messages) % 2 == 1:  # 且为奇数，则上次可能异常退出
            padding_content = '上次会话异常结束，请继续交流'
            st_object.session_state.messages.append({'role': LLM_ROBOT_ROLE, 'content': padding_content})
            update_conversation_time(st_object.session_state.conversation_id)
            create_message(st_object.session_state.conversation_id, LLM_ROBOT_ROLE, padding_content)

def show_history_conversations(st_object, user_name, generator):
    conversation_history: dict = get_conversation_dict(user_name)
    # 显示多个 sidebar，并确保只能选择一个
    for k, v in conversation_history.items():
        if len(v) > 0:
            generator.markdown(f"### {k}")
            select_zip = zip([str(i['id']) for i in v], [str(i['theme']) for i in v])
            for id, theme in select_zip:
                # 用会话的第一条消息作为主题概括，只展示前15个字符，不然会跨行
                if generator.button(theme[:7]+'...', use_container_width=True, key=id):  # 防止请求返回过程中被打断
                    # 一旦操作就把trigger都置为False，并让机器停止思考激活输入框
                    st_object.session_state.thinking = False
                    st_object.session_state.conversation_id = id
                    messages = get_message_via_cid(st_object.session_state.conversation_id)
                    adj_messages = [
                        {'role': LLM_ROBOT_ROLE if i['sender'] == LLM_ROBOT_ROLE else LLM_USER_ROLE,
                         'content': i['message']} for i in messages]
                    st_object.session_state.messages = adj_messages  # 更新当前的消息列表
                    fix_abnormal_chat(st_object)  # 修复异常会话