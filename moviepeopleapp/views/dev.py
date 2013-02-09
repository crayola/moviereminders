def load_sample_db(request):
    import moviepeopleapp.APIparser as APIparser
    log.info('Parsing!')
    [APIparser.parseMovie(x) for x in range(1000)]
    log.info('Done parsing.')
    APIparser.buildImportance(1, 10000)
    log.info('Done building importance.')
    return HttpResponse('All done! Now please rebuild the index: manage.py rebuild_index.')