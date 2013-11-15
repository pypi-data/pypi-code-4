# -*- coding: utf-8 -*-
from modeltranslation.translator import translator, TranslationOptions
from .models import Category, Page


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'slug', 'short_description', 'description',)


class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'synopsis', 'content',)


translator.register(Category, CategoryTranslationOptions)
translator.register(Page, PageTranslationOptions)
