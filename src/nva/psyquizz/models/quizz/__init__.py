# -*- coding: utf-8 -*-

from nva.psyquizz.extra_questions import generate_extra_questions
from zope.location import Location
import zope.schema


class QuizzBase(Location):

    @classmethod
    def base_fields(cls, course):
        fields = zope.schema.getFieldsInOrder(cls.__schema__)
        for name, field in fields:
            yield field

    @classmethod
    def criteria_fields(cls, course):
        for criteria in course.criterias:
            values = zope.schema.vocabulary.SimpleVocabulary([
                zope.schema.vocabulary.SimpleTerm(
                    value=c.strip(), token=idx, title=c.strip())
                    for idx, c in enumerate(criteria.items.split('\n'), 1)
                    if c.strip()])

            yield zope.schema.Choice(
                __name__='criteria_%s' % criteria.id,
                title=criteria.title,
                description=u"Wählen Sie das Zutreffende aus.",
                vocabulary=values,
                required=True,
            )

    @classmethod
    def extra_fields(cls, course):
        questions_text = course.extra_questions
        if questions_text:
            for field in generate_extra_questions(questions_text):
                yield field

    @classmethod
    def additional_extra_fields(cls, course):
        from nva.psyquizz.models.interfaces import source_fixed_extra_questions 
        feq = source_fixed_extra_questions(None)
        for eqs in course.fixed_extra_questions:
            term = feq.getTerm(eqs)
            yield term.iface
