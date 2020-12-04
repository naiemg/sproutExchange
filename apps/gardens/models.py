from django.db import models
from django.utils.text import slugify
from datetime import datetime, timedelta 

class Garden(models.Model):
	name = models.CharField(max_length=255)
	owner = models.ForeignKey('userauth.UserProfile', on_delete=models.CASCADE, blank=True, null=True)
	description = models.TextField()
	amount_raised = models.IntegerField(default=0)
	total_backers = models.IntegerField(default=0)
	date_created = models.DateTimeField(auto_now_add=True)
	active = models.BooleanField(default=True)
	sponsor_deadline = models.DateTimeField(auto_now_add=False)
	
	def __str__(self):
		return self.name

class Tier(models.Model):
	name = models.CharField(max_length = 255)
	description = models.TextField()
	price_per_share = models.PositiveSmallIntegerField(default=0)
	total_shares = models.IntegerField()
	total_shares_remaining = models.PositiveIntegerField(blank=True, null=True) #How many shares remaining that users can purchase
	num_backers = models.IntegerField(default=0)
	estimated_harvest = models.DateTimeField(auto_now_add=False)
	garden = models.ForeignKey(Garden, on_delete=models.CASCADE, blank=True, null=True)
	
	def save(self, *args, **kwargs):
		if self.total_shares_remaining == None:
			# look to see if this is the initial save
			# if it is then all shares issued should also be available for purchase
			self.total_shares_remaining = self.total_shares
		else:
			pass
		
		super(Tier, self).save(*args, **kwargs)

	def __str__(self):
		return self.name

class Update(models.Model):
	garden = models.ForeignKey(Garden, on_delete=models.CASCADE, blank=True, null=True)
	title = models.CharField(max_length=255)
	text = models.TextField()
	date_published = models.DateTimeField(auto_now_add=True)
	slug = models.SlugField(max_length=255, blank=True, null=True)

	def save(self, *args, **kwargs):
		if self.slug is None:
			self.slug = slugify(self.title)
		super(Update,self).save(*args, **kwargs)
	
	def __str__(self):
		return self.title

class Comment(models.Model):
	author = models.ForeignKey('userauth.UserProfile', on_delete=models.CASCADE, blank=True, null=True)
	update = models.ForeignKey(Update, on_delete=models.CASCADE, blank=True, null=True)
	text = models.TextField()
	date_published = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.text