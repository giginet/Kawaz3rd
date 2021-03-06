# ! -*- coding: utf-8 -*-
#
#
#
from django.contrib.contenttypes.models import ContentType
from django_comments.models import Comment
from kawaz.core.personas.models import Persona
from activities.models import Activity
from activities.mediator import ActivityMediator



class ProjectActivityMediator(ActivityMediator):

    m2m_fields = (
        'members',
    )

    def alter(self, instance, activity, **kwargs):
        # 状態が draft の場合は通知しない
        if activity and instance.pub_state == 'draft':
            return None
        if activity and activity.status == 'updated':
            if activity.previous:
                # 通知が必要な状態の変更を詳細に記録する
                previous = activity.previous.snapshot
                is_created = lambda x: (
                    not getattr(previous, x) and
                    getattr(instance, x)
                )
                is_updated = lambda x: (
                    getattr(previous, x) and
                    getattr(instance, x) and
                    getattr(previous, x) != getattr(instance, x)
                )
                is_deleted = lambda x: (
                    getattr(previous, x) and
                    not getattr(instance, x)
                )
                remarks = []
                attributes = (
                    'title',
                    'body',
                    'icon',
                    'status',
                    'category',
                )
                for attribute in attributes:
                    if is_created(attribute):
                        remarks.append(attribute + '_created')
                    elif is_updated(attribute):
                        remarks.append(attribute + '_updated')
                    elif is_deleted(attribute):
                        remarks.append(attribute + '_deleted')
                if not remarks:
                    # 通知が必要な変更ではないため通知しない
                    return None
                activity.remarks = "\n".join(remarks)
        elif activity is None:
            # m2m_updated
            action = kwargs.get('action')
            model = kwargs.get('model')
            if action not in ('post_add', 'post_remove'):
                # 追加/削除以外は通知しない
                return None
            if action == 'post_add' and instance.members.count() == 1:
                # models.join_administratorシグナルによりpost_save処理より以前に
                # 作成者参加が行われ project が作成される前に参加者が追加される
                # したがって参加者が一人（join_administratorにより追加された直後）
                # の場合に飛んできた m2m_signal は無視
                return None
            # 追加・削除をトラックするActivityを作成
            ct = ContentType.objects.get_for_model(instance)
            status = 'user_added' if action == 'post_add' else 'user_removed'
            activity = Activity(content_type=ct,
                                object_id=instance.pk,
                                status=status)
            # snapshot を保存
            activity.snapshot = instance
            # 追加・削除されたユーザーのIDを保存
            activity.remarks = " ".join(map(str, kwargs.get('pk_set')))
        return activity

    def prepare_context(self, activity, context, typename=None):
        context = super().prepare_context(activity, context, typename)

        if activity.status == 'updated':
            # remarks に保存された変更状態を利便のためフラグ化
            for flag in activity.remarks.split():
                context[flag] = True
        elif activity.status in ('user_added', 'user_removed'):
            # ユーザーの追加・削除状態だった場合は誰が追加されたのかを設定
            # 基本的に今の仕様では同時に一人までしか追加できないはずだが、
            # {{ user.nickname }}さんと他{{ user_count | add:"-1" }}名
            # みたいな感じで表示できるようにしている
            pk_set = map(int, activity.remarks.split())
            users = Persona.objects.filter(pk__in=(pk_set))
            context['users'] = users
            context['user'] = users[0]
            context['user_count'] = users.count()
        elif activity.status == 'comment_added':
            # コメントが付いたとき、remarksにcommentのpkが入ってるはずなので
            # 取得してcontextに渡す
            try:
                comment = Comment.objects.get(pk=int(activity.remarks))
                context['comment'] = comment
            except:
                pass
        return context
