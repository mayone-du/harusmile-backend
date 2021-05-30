import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import graphql_jwt
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id
from .models import User, Tag, Profile, Post, Review, Message, Address, Gender
from graphene_file_upload.scalars import Upload



class UserNode(DjangoObjectType):
  class Meta:
    model = User
    filter_fields = {
      'email': ['exact', 'icontains'],
    }
    interfaces = (relay.Node,)


class TagNode(DjangoObjectType):
  class Meta:
    model = Tag
    filter_fields = {
      'tag_name': ['exact', 'icontains'],
    }
    interfaces = (relay.Node,)


class GenderNode(DjangoObjectType):
  class Meta:
    model = Gender
    filter_fields = {
      'gender_name': ['exact', 'icontains'],
    }
    interfaces = (relay.Node,)


class AddressNode(DjangoObjectType):
  class Meta:
    model = Address
    filter_fields = {
      'address_name': ['exact', 'icontains'],
    }
    interfaces = (relay.Node,)



class ProfileNode(DjangoObjectType):
  class Meta:
    model = Profile
    filter_fields = {
      'profile_name': ['exact', 'icontains'],
      'is_college_student': ['exact',],
      'school_name': ['exact', 'icontains'],
      'selected_address': ['exact'],
      'selected_gender': ['exact'],
    }
    interfaces = (relay.Node,)


class PostNode(DjangoObjectType):
  class Meta:
    model = Post
    filter_fields = {
      'title': ['exact', 'icontains'],
      'content': ['exact', 'icontains'],
    }
    interfaces = (relay.Node,)


class MessageNode(DjangoObjectType):
  class Meta:
    model = Message
    filter_fields = {
      'text': ['exact', 'icontains'],
    }
    interfaces = (relay.Node,)


class ReviewNode(DjangoObjectType):
  class Meta:
    model = Review
    filter_fields = {
      'stars': ['exact'],
      'review_text': ['exact', 'icontains'],
    }
    interfaces = (relay.Node,)



class CreateUserMutation(relay.ClientIDMutation):
  class Input:
    email = graphene.String(required=True)
    password = graphene.String(required=True)

  user = graphene.Field(UserNode)

  def mutate_and_get_payload(root, info, **input):
    user = User(
      email=input.get('email'),
    )
    user.set_password(input.get('password'))
    user.save()

    return CreateUserMutation(user=user)


class CreateProfileMutation(relay.ClientIDMutation):
  class Input:
    profile_name = graphene.String(required=True)
    is_college_student = graphene.Boolean(required=True)
    school_name = graphene.String(required=True)
    selected_gender = graphene.ID(required=True)
    selected_address = graphene.ID(required=True)


  profile = graphene.Field(ProfileNode)

  @login_required
  def mutate_and_get_payload(root, info, **input):
    profile = Profile(
      target_user_id=info.context.user.id,
      profile_name = input.get('profile_name'),
      is_college_student = input.get('is_college_student'),
      school_name = input.get('school_name'),
      selected_gender = input.get('selected_gender'),
      selected_address = input.get('selected_address'),
    )
    profile.save()

    return CreateProfileMutation(profile=profile)


class UpdateProfileMutation(relay.ClientIDMutation):
  class Input:
    id = graphene.ID(required=True)
    profile_name = graphene.String(required=True)
    is_college_student = graphene.Boolean(required=True)
    school_name = graphene.String(required=True)
    selected_gender = graphene.ID(required=True)
    selected_address = graphene.ID(required=True)
    following_users = graphene.List(graphene.ID)
    tags = graphene.List(graphene.ID)

  profile = graphene.Field(ProfileNode)

  @login_required
  def mutate_and_get_payload(root, info, **input):
    profile = Profile(
      id = from_global_id(input.get('id'))[1],
      profile_name = input.get('profile_name'),
      is_college_student = input.get('is_college_student'),
      school_name = input.get('school_name'),
      gender = input.get('gender'),
      tags = input.get('tags'),
    )
    if input.get('following_users') is not None:
      followings_set = []
      for user in input.get('following_users'):
        followings_id = from_global_id(user)[1]
        user_object = User.objects.get(id=followings_id)
        followings_set.append(user_object)
        profile.followings.set(followings_set)
      profile.save()
      
    if input.get('tags') is not None:
      tag_set = []
      for tag in input.get('tags'):
        tag_id = from_global_id(tag)[1]
        tag_object = Tag.objects.get(id=tag_id)
        tag_set.append(tag_object)
        profile.tags.set(tag_set)
      profile.save()
    profile.save()
    
    return UpdateProfileMutation(profile=profile)



class CreatePostMutation(relay.ClientIDMutation):
  class Input:
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    post_image = Upload(required=False)
    is_published = graphene.Boolean(required=True)
    
  post = graphene.Field(PostNode)

  @login_required
  def mutate_and_get_payload(root, info, **input):
    post = Post(
      posted_user_id=info.context.user.id,
      title = input.get('title'),
      content = input.get('content'),
      post_image = input.get('post_image'),
      is_published = input.get('is_published'),
    )

    return CreatePostMutation(post=post)


class UpdatePostMutation(relay.ClientIDMutation):
  class Input:
    id = graphene.ID(required=True)
    title = graphene.String(required=False)
    content = graphene.String(required=False)
    post_image = Upload(required=False)
    is_published = graphene.Boolean(required=False)

  post = graphene.Field(PostNode)

  @login_required
  def mutate_and_get_payload(root, info, **input):
    post = Post(
      id = from_global_id(input.get('id'))[1],
      title = input.get('title'),
      content = input.get('content'),
      post_image = input.get('post_image'),
      is_published = input.get('is_published'),
    )
    return UpdatePostMutation(post=post)



class DeletePostMutation(relay.ClientIDMutation):
  class Input:
    id = graphene.ID(required=True)

  post = graphene.Field(PostNode)

  @login_required
  def mutate_and_get_payload(root, info, **input):
    post = Post(
      id=from_global_id(input.get('id'))[1],
    )
    post.delete()
    return DeletePostMutation(post=post)



class CreateMessageMutation(relay.ClientIDMutation):
  class Input:
    distination = graphene.ID(required=True)
    text = graphene.String(required=True)
  
  message = graphene.Field(MessageNode)
    
  @login_required
  def mutate_and_get_payload(root, info, **input):
    message = Message(
      sender_user_id=info.context.user.id,
      distination = User.objects.get(from_global_id(input.get('distination'))[1])
    )
    return CreateMessageMutation(message=message)
  

class CreateReviewMutation(relay.ClientIDMutation):
  class Input:
    target_post = graphene.ID(required=True)
    review_text = graphene.String(required=True)
    stars = graphene.Int(required=True)

  review = graphene.Field(ReviewNode)

  @login_required
  def mutate_and_get_payload(root, info, **input):
    review = Review(
      target_post = from_global_id(input.get('target_post'))[1],
      reviewed_user_id = info.context.user.id,
      review_text = input.get('review_text'),
      stars = input.get('stars'),
    )
    
    return CreateReviewMutation(review=review)




class Mutation(graphene.ObjectType):
  create_user = CreateUserMutation.Field()
  create_profile = CreateProfileMutation.Field()
  update_profile = UpdateProfileMutation.Field()
  create_post = CreatePostMutation.Field()
  update_post = UpdatePostMutation.Field()
  delete_post = DeletePostMutation.Field()
  create_message = CreateMessageMutation.Field()
  token_auth = graphql_jwt.ObtainJSONWebToken.Field()
  refresh_token = graphql_jwt.Refresh.Field()


class Query(graphene.ObjectType):
  user = graphene.Field(UserNode, id=graphene.NonNull(graphene.ID))
  all_users = DjangoFilterConnectionField(UserNode)
  profile = graphene.Field(ProfileNode, id=graphene.NonNull(graphene.ID))
  all_profiles = DjangoFilterConnectionField(ProfileNode)
  post = graphene.Field(PostNode, id=graphene.NonNull(graphene.ID))
  all_posts = DjangoFilterConnectionField(PostNode)
  tag = graphene.Field(TagNode, id=graphene.NonNull(graphene.ID))
  all_tags = DjangoFilterConnectionField(TagNode)
  review = graphene.Field(ReviewNode, id=graphene.NonNull(graphene.ID))
  all_reviews = DjangoFilterConnectionField(ReviewNode)
  gender = graphene.Field(GenderNode, id=graphene.NonNull(graphene.ID))
  all_genders = DjangoFilterConnectionField(GenderNode)
  address = graphene.Field(AddressNode, id=graphene.NonNull(graphene.ID))
  all_addresses = DjangoFilterConnectionField(AddressNode)

  

  # user
  @login_required
  def resolve_user(self, info, **kwargs):
    email = kwargs.get('email')
    return get_user_model().objects.get(id=from_global_id(id)[1])
    
  @login_required
  def resolve_all_users(self, info, **kwargs):
    return get_user_model().objects.all()

  # profile
  @login_required
  def resolve_profile(self, info, **kwargs):
    id = kwargs.get('id')
    if id is not None:
      return Profile.objects.get(id=from_global_id(id)[1])

  @login_required
  def resolve_all_profiles(self, info, **kwargs):
    return Profile.objects.all()

  # post
  @login_required
  def resolve_post(self, info, **kwargs):
    id = kwargs.get('id')
    if id is not None:
      return Post.objects.get(id=from_global_id(id)[1])

  @login_required
  def resolve_all_posts(self, info, **kwargs):
    return Post.objects.all()


  # gender
  @login_required
  def resolve_gender(self, info, **kwargs):
    id = kwargs.get('id')
    if id is not None:
      return Gender.objects.get(id=from_global_id(id)[1])

  @login_required
  def resolve_all_genders(self, info, **kwargs):
    return Gender.objects.all()


  # address
  @login_required
  def resolve_address(self, info, **kwargs):
    id = kwargs.get('id')
    if id is not None:
      return Address.objects.get(id=from_global_id(id)[1])

  @login_required
  def resolve_all_addresses(self, info, **kwargs):
    return Address.objects.all()

  # tag
  @login_required
  def resolve_tag(self, info, **kwargs):
    id = kwargs.get('id')
    if id is not None:
      return Tag.objects.get(id=from_global_id(id)[1])

  @login_required
  def resolve_all_tags(self, info, **kwargs):
    return Tag.objects.all()

  # review
  @login_required
  def resolve_review(self, info, **kwargs):
    id = kwargs.get('id')
    if id is not None:
      return Review.objects.get(id=from_global_id(id)[1])

  @login_required
  def resolve_all_reviews(self, info, **kwargs):
    return Review.objects.all()

  # message
  @login_required
  def resolve_message(self, info, **kwargs):
    id = kwargs.get('id')
    if id is not None:
      return Message.objects.get(id=from_global_id(id)[1])

  @login_required
  def resolve_all_messages(self, info, **kwargs):
    return Message.objects.all()

