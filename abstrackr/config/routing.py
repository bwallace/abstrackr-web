"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE
    map.connect('/help/', controller='static_pages', action='help')
    map.connect('/citing/', controller='static_pages', action='citing')

    map.connect('/{controller}/{action}')
    map.connect('/review/add_notes/{study_id}', controller='review', action='add_notes')
    map.connect('/review/delete_assignment/{review_id}/{assignment_id}', controller='review', action='delete_assignment')
    map.connect('/review/add_admin/{project_id}/{user_id}', controller='review', action='add_admin')
    map.connect('/review/remove_admin/{project_id}/{user_id}', controller='review', action='remove_admin')
    map.connect('/review/get_fields/{review_id}', controller='review', action='get_fields')

    map.connect('/review/update_tags/{study_id}/{tag_privacy}', controller='review', action='update_tags')

    map.connect('/review/update_tag_types/{review_id}/{study_id}', controller='review', action='update_tag_types')
    map.connect('/review/edit_tags/{review_id}/{assignment_id}', controller='review', action='edit_tags')
    map.connect('/review/edit_tag/{tag_id}/{assignment_id}', controller='review', action='edit_tag')
    map.connect('/review/delete_tag/{tag_id}/{assignment_id}', controller='review', action='delete_tag')
    map.connect('/review/delete_term/{term_id}/{assignment_id}', controller='review', action='delete_term')
    map.connect('/review/admin/{project_id}', controller='review', action='admin')
    map.connect('/{controller}/{action}/{id}')
    map.connect('/screen/{review_id}/{assignment_id}', controller='review', action='screen')
    map.connect('/screen_next/{review_id}/{assignment_id}', controller='review', action='screen_next')
    map.connect('/label/{review_id}/{assignment_id}/{study_id}/{seconds}/{label}', controller='review', action='label_citation')

    map.connect('/next_citation/{review_id}/{assignment_id}', controller='review', action='get_next_citation_fragment')

    map.connect('/markup/{id}/{assignment_id}/{citation_id}', controller='review', action='markup_citation')
    map.connect('/label_term/{review_id}/{label}', controller='review', action='label_term')
    map.connect('/relabel_term/{term_id}/{assignment_id}/{new_label}', controller='review', action='relabel_term')
    map.connect('/review_my_labels/{review_id}', controller='review', action='review_labels')
    map.connect('/review_my_labels/{review_id}/{assignment_id}', controller='review', action='review_labels')
    map.connect('/review/review_terms/{id}/{assignment_id}', controller='review', action='review_terms')
    map.connect('/show_label/{review_id}/{citation_id}/{assignment_id}', controller='review', action='show_labeled_citation')
    map.connect('/review/remove_from_review/{reviewer_id}/{review_id}', controller='review', action='remove_from_review')
    map.connect('/review/tag_citation/{review_id}/{study_id}', controller='review', action='tag_citation')

    map.connect('/join/{review_code}', controller='review', action='join')
    map.connect('/', controller='trackr', action='start')

    return map
