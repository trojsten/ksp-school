import school


def version(request):
    return {"SCHOOL_VERSION": school.VERSION}
