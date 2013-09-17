from curdling.maestro import Maestro


def test_maestro_pending_packages():
    "Maestro will keep the reference of a package if its not done or failed"

    # Given that I have a maestro
    maestro = Maestro()

    # When I file a package under it
    maestro.file_package('curdling', dependency_of=None)

    # Then I see it's still waiting for the dependency checking
    maestro.pending_packages.should.equal(['curdling'])


def test_maestro_pending_packages_no_deps():
    "It shoudl be possible to mark packages as built maestro"

    # Given that I have a maestro with a package filed under it
    maestro = Maestro()
    maestro.file_package('curdling', dependency_of=None)

    # When and I mark the package as `checked`,
    # meaning that all the dependencies were checked
    maestro.mark_built('curdling', '')

    # Then I see it's still waiting for the dependency checking
    maestro.pending_packages.should.equal([])
    maestro.built.should.equal({'curdling'})


def test_maestro_mark_failed():
    "It shoudl be possible to mark packages as failed in the maestro"

    # Given that I have a maestro with a package filed under it
    maestro = Maestro()
    maestro.file_package('curdling', dependency_of=None)

    # When and I mark the package as `failed`, meaning that all the
    # dependencies were checked
    maestro.mark_failed('curdling', '')

    # Then I see it's still waiting for the dependency checking
    maestro.pending_packages.should.equal([])
    maestro.failed.should.equal({'curdling'})


def test_maestro_should_queue():
    "Our maestro should know if a package can be queued or not"

    # Given that I have an empty maestro
    maestro = Maestro()

    # When I check if I can queue a package that is *not* present in the
    # maestro instance, Then I see it returns true
    maestro.should_queue('curdling').should.be.true

    # After filing this package to the maestro, should_queue will change its
    # results, as you can see here.
    maestro.file_package('curdling', dependency_of=None)
    maestro.should_queue('curdling').should.be.false


def test_maestro_mark_built_update_mapping():

    # Given that I have a maestro with a couple packages filed under it
    maestro = Maestro()
    maestro.file_package('curdling', dependency_of=None)
    maestro.file_package('sure (== 0.1.2)', dependency_of='curdling')
    maestro.file_package('forbiddenfruit (> 0.1.0)', dependency_of='curdling')
    maestro.file_package('forbiddenfruit (>= 0.1.2)', dependency_of='sure (== 0.1.2)')

    # Wehn I mark the files as built
    maestro.mark_built('curdling', '/curds/curdling.whl')
    maestro.mark_built('sure (== 0.1.2)', '/curds/sure.whl')
    maestro.mark_built('forbiddenfruit (> 0.1.0)', '/curds/forbiddenfruit.whl')
    maestro.mark_built('forbiddenfruit (>= 0.1.2)', '/curds/forbiddenfruit.whl')

    # Then I see I still have just one entry in the mapping
    dict(maestro.mapping).should.equal({
        'curdling': {
            None: {
                'dependency_of': None,
                'data': '/curds/curdling.whl',
            },
        },
        'sure': {
            '== 0.1.2': {
                'dependency_of': 'curdling',
                'data': '/curds/sure.whl'
            },
        },
        'forbiddenfruit': {
            '> 0.1.0': {
                'dependency_of': 'curdling',
                'data': '/curds/forbiddenfruit.whl',
            },
            '>= 0.1.2': {
                'dependency_of': 'sure (== 0.1.2)',
                'data': '/curds/forbiddenfruit.whl',
            },
        },
    })


def test_maestro_get_data():
    "It should be possible to retrieve data of a given requirement"

    # Given that I have a maestro filled with a package
    maestro = Maestro()
    maestro.mapping = {
        'forbiddenfruit': {
            '> 0.1.0': {
                'dependency_of': None,
                'data': '/curds/forbiddenfruit.whl',
            },
        }
    }

    # When I retrieve the data from the following requirement
    data = maestro.get_data('forbiddenfruit (> 0.1.0)')

    # Then I see the correct value retrieved
    data.should.equal('/curds/forbiddenfruit.whl')
