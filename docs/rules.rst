Rules
=====

Base rule
---------

.. autoclass:: hammurabi.rules.base.Rule
   :noindex:


Attributes
----------

OwnerChanged
~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.attributes.OwnerChanged
   :noindex:

ModeChanged
~~~~~~~~~~~

.. autoclass:: hammurabi.rules.attributes.ModeChanged
   :noindex:

Directories
-----------

DirectoryExists
~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.directories.DirectoryExists
   :noindex:

DirectoryNotExists
~~~~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.directories.DirectoryNotExists
   :noindex:

DirectoryEmptied
~~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.directories.DirectoryEmptied
   :noindex:

Files
-----

FileExists
~~~~~~~~~~

.. autoclass:: hammurabi.rules.files.FileExists
   :noindex:

FilesExist
~~~~~~~~~~

.. autoclass:: hammurabi.rules.files.FilesExist
   :noindex:

FileNotExists
~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.files.FileNotExists
   :noindex:

FilesNotExist
~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.files.FilesNotExist
   :noindex:

FileEmptied
~~~~~~~~~~~

.. autoclass:: hammurabi.rules.files.FileEmptied
   :noindex:

Ini files
---------

SectionExists
~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.ini.SectionExists
   :noindex:

SectionNotExists
~~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.ini.SectionNotExists
   :noindex:

SectionRenamed
~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.ini.SectionRenamed
   :noindex:

OptionsExist
~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.ini.OptionsExist
   :noindex:

OptionsNotExist
~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.ini.OptionsNotExist
   :noindex:

OptionRenamed
~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.ini.OptionRenamed
   :noindex:

Json files
----------

JsonKeyExists
~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.json.JsonKeyExists
   :noindex:

JsonKeyNotExists
~~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.json.JsonKeyNotExists
   :noindex:

JsonKeyRenamed
~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.json.JsonKeyRenamed
   :noindex:

JsonValueExists
~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.json.JsonValueExists
   :noindex:

JsonValueNotExists
~~~~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.json.JsonValueNotExists
   :noindex:

Operations
----------

Moved
~~~~~

.. autoclass:: hammurabi.rules.operations.Moved
   :noindex:

Renamed
~~~~~~~

.. autoclass:: hammurabi.rules.operations.Renamed
   :noindex:

Copied
~~~~~~

.. autoclass:: hammurabi.rules.operations.Copied
   :noindex:

Templates
---------

TemplateRendered
~~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.templates.TemplateRendered
   :noindex:

Text files
----------

LineExists
~~~~~~~~~~

.. autoclass:: hammurabi.rules.text.LineExists
   :noindex:

LineNotExists
~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.text.LineNotExists
   :noindex:

LineReplaced
~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.text.LineReplaced
   :noindex:

Yaml files
----------

YamlKeyExists
~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.yaml.YamlKeyExists
   :noindex:

YamlKeyNotExists
~~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.yaml.YamlKeyNotExists
   :noindex:

YamlKeyRenamed
~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.yaml.YamlKeyRenamed
   :noindex:

YamlValueExists
~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.yaml.YamlValueExists
   :noindex:

YamlValueNotExists
~~~~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.yaml.YamlValueNotExists
   :noindex:

TOML files
----------

.. warning::

    In case of a single line toml file, the parser used in hammurabi will only
    keep the comment if the file contains a newline character.

TomlKeyExists
~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.toml.TomlKeyExists
   :noindex:

TomlKeyNotExists
~~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.toml.TomlKeyNotExists
   :noindex:

TomlKeyRenamed
~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.toml.TomlKeyRenamed
   :noindex:

TomlValueExists
~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.toml.TomlValueExists
   :noindex:

TomlValueNotExists
~~~~~~~~~~~~~~~~~~

.. autoclass:: hammurabi.rules.toml.TomlValueNotExists
   :noindex:
