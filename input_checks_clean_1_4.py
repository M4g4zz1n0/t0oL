import json
import os


def read_json(path):
    if not os.path.isfile(path):
        return None, f"Il file '{path}' non esiste."

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError:
        return None, f"Non è possibile leggere il file '{path}'."
    except json.JSONDecodeError as e:
        return None, f"Il file '{path}' non contiene un JSON valido (riga {e.lineno}, colonna {e.colno})."

    return data, None


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_cardinality(cardinality, where, errors):
    if not isinstance(cardinality, dict):
        errors.append(f"{where}: cardinality deve essere un oggetto.")
        return

    if "min" not in cardinality or "max" not in cardinality:
        errors.append(f"{where}: cardinality deve contenere min e max.")
        return

    min_value = cardinality["min"]
    max_value = cardinality["max"]

    if not isinstance(min_value, int) or isinstance(min_value, bool) or min_value < 0:
        errors.append(f"{where}: cardinality.min deve essere un intero non negativo.")

    if max_value != "N":
        if not isinstance(max_value, int) or isinstance(max_value, bool) or max_value < 1:
            errors.append(f"{where}: cardinality.max deve essere un intero positivo oppure 'N'.")
        elif isinstance(min_value, int) and not isinstance(min_value, bool) and min_value > max_value:
            errors.append(f"{where}: cardinality.min non può essere maggiore di cardinality.max.")


def check_attributes(attributes, where, errors):
    if not isinstance(attributes, list):
        errors.append(f"{where}: attributes deve essere una lista.")
        return []

    names = []
    allowed_types = ["string", "integer", "number", "boolean", "date", "time", "datetime"]

    for i in range(len(attributes)):
        attribute = attributes[i]
        current = f"{where}.attributes[{i}]"

        if not isinstance(attribute, dict):
            errors.append(f"{current}: l'attributo deve essere un oggetto.")
            continue

        name = attribute.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{current}: name mancante o non valido.")
            continue

        if name in names:
            errors.append(f"{where}: attributo '{name}' duplicato.")
        else:
            names.append(name)

        if attribute.get("type") not in allowed_types:
            errors.append(f"{current}: type non valido.")

        if "cardinality" not in attribute:
            errors.append(f"{current}: cardinality mancante.")
        else:
            check_cardinality(attribute["cardinality"], current, errors)

    return names


def check_er_schema(er_schema):
    errors = []

    if not isinstance(er_schema, dict):
        return ["Il file ER deve contenere un oggetto JSON."]

    if er_schema.get("format_version") != "1.0":
        errors.append("er_schema: format_version deve essere '1.0'.")

    entities = er_schema.get("entities")
    relationships = er_schema.get("relationships")

    if not isinstance(entities, list) or len(entities) == 0:
        errors.append("er_schema: entities deve essere una lista non vuota.")
        entities = []

    if not isinstance(relationships, list):
        errors.append("er_schema: relationships deve essere una lista.")
        relationships = []

    entity_names = []
    entity_attributes = {}
    identifiers = {}

    for i in range(len(entities)):
        entity = entities[i]
        current = f"entities[{i}]"

        if not isinstance(entity, dict):
            errors.append(f"{current}: l'entità deve essere un oggetto.")
            continue

        name = entity.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{current}: name mancante o non valido.")
            continue

        if name in entity_names:
            errors.append(f"er_schema: entità '{name}' duplicata.")
        else:
            entity_names.append(name)

        entity_attributes[name] = check_attributes(entity.get("attributes"), current, errors)

        identifier = entity.get("identifier")
        if not isinstance(identifier, list) or len(identifier) == 0:
            errors.append(f"{current}: identifier deve essere una lista non vuota.")
            identifiers[name] = []
            continue

        identifiers[name] = []
        for value in identifier:
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{current}: identifier contiene un valore non valido.")
            elif value in identifiers[name]:
                errors.append(f"{current}: '{value}' compare più volte nell'identifier.")
            else:
                identifiers[name].append(value)

    relationship_names = []
    relation_entities = {}

    for i in range(len(relationships)):
        relationship = relationships[i]
        current = f"relationships[{i}]"

        if not isinstance(relationship, dict):
            errors.append(f"{current}: la relazione deve essere un oggetto.")
            continue

        name = relationship.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{current}: name mancante o non valido.")
            continue

        if name in relationship_names:
            errors.append(f"er_schema: relazione '{name}' duplicata.")
        else:
            relationship_names.append(name)

        sides = relationship.get("sides")
        if not isinstance(sides, list) or len(sides) != 2:
            errors.append(f"{current}: sides deve contenere esattamente due lati.")
            sides = []

        current_entities = []
        roles = []

        for j in range(len(sides)):
            side = sides[j]
            side_where = f"{current}.sides[{j}]"

            if not isinstance(side, dict):
                errors.append(f"{side_where}: il lato deve essere un oggetto.")
                continue

            entity = side.get("entity")
            if entity not in entity_names:
                errors.append(f"{side_where}: entità '{entity}' non presente nello schema.")
            else:
                current_entities.append(entity)

            if "cardinality" not in side:
                errors.append(f"{side_where}: cardinality mancante.")
            else:
                check_cardinality(side["cardinality"], side_where, errors)

            role = None
            if "role" in side:
                role = side["role"]
                if not isinstance(role, str) or not role.strip():
                    errors.append(f"{side_where}: role non valido.")
            roles.append(role)

        if len(current_entities) == 2:
            relation_entities[name] = current_entities

            if current_entities[0] == current_entities[1]:
                if len(roles) != 2 or roles[0] is None or roles[1] is None:
                    errors.append(f"{current}: una self-relationship deve specificare i due role.")
                elif roles[0] == roles[1]:
                    errors.append(f"{current}: i role della self-relationship devono essere differenti.")

        check_attributes(relationship.get("attributes"), current, errors)

    for entity in identifiers:
        incident = []
        for relationship in relation_entities:
            if entity in relation_entities[relationship]:
                incident.append(relationship)

        for value in identifiers[entity]:
            attribute = value in entity_attributes.get(entity, [])
            relationship = value in incident

            if not attribute and not relationship:
                errors.append(f"Entità '{entity}': '{value}' nell'identifier non è un attributo né una relazione incidente.")
            elif attribute and relationship:
                errors.append(f"Entità '{entity}': '{value}' nell'identifier è ambiguo.")

    return errors


def er_data(er_schema):
    entities = []
    attributes = {}
    relationships = {}
    relationship_attributes = {}

    for entity in er_schema.get("entities", []):
        name = entity["name"]
        entities.append(name)
        attributes[name] = []
        for attribute in entity.get("attributes", []):
            attributes[name].append(attribute["name"])

    for relationship in er_schema.get("relationships", []):
        name = relationship["name"]
        relationships[name] = []
        relationship_attributes[name] = []

        for side in relationship.get("sides", []):
            relationships[name].append(side["entity"])

        for attribute in relationship.get("attributes", []):
            relationship_attributes[name].append(attribute["name"])

    return entities, attributes, relationships, relationship_attributes


def check_path(path, target_entity, entities, relationships, where, errors):
    if not isinstance(path, list) or len(path) == 0:
        errors.append(f"{where}: il percorso deve essere una lista non vuota.")
        return

    first = path[0]
    if not isinstance(first, dict) or first.get("entity") not in entities:
        errors.append(f"{where}[0]: entità iniziale mancante o non valida.")
        return

    if first["entity"] != target_entity:
        errors.append(f"{where}: il percorso deve iniziare da '{target_entity}'.")

    current_entity = first["entity"]

    for i in range(1, len(path)):
        step = path[i]
        current = f"{where}[{i}]"

        if not isinstance(step, dict):
            errors.append(f"{current}: il passo deve essere un oggetto.")
            continue

        relationship = step.get("relationship")
        entity = step.get("entity")

        if not isinstance(relationship, str):
            errors.append(f"{current}: relationship deve essere una stringa.")
            continue

        if relationship not in relationships:
            errors.append(f"{current}: relazione '{relationship}' non presente nello schema ER.")
            continue

        sides = relationships[relationship]
        if current_entity not in sides or entity not in sides:
            errors.append(f"{current}: '{relationship}' non collega '{current_entity}' a '{entity}'.")
        elif sides[0] != sides[1] and current_entity == entity:
            errors.append(f"{current}: il percorso non attraversa correttamente '{relationship}'.")

        if "remote_fraction_if_separate" in step:
            value = step["remote_fraction_if_separate"]
            if not is_number(value) or value < 0 or value > 1:
                errors.append(f"{current}: remote_fraction_if_separate deve essere compreso tra 0 e 1.")

        current_entity = entity


def check_labeled_schema(labeled_schema):
    errors = []

    if not isinstance(labeled_schema, dict):
        return ["Il file dello schema etichettato deve contenere un oggetto JSON."]

    if labeled_schema.get("format_version") != "1.0":
        errors.append("labeled_schema: format_version deve essere '1.0'.")

    if "candidate_id" in labeled_schema:
        candidate_id = labeled_schema["candidate_id"]
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append("labeled_schema: candidate_id non valido.")

    if "technology" in labeled_schema:
        technology = labeled_schema["technology"]
        if not isinstance(technology, dict):
            errors.append("labeled_schema: technology deve essere un oggetto.")
        else:
            if technology.get("name") not in ["mongodb", "couchbase"]:
                errors.append("labeled_schema: technology.name deve essere 'mongodb' oppure 'couchbase'.")
            if not isinstance(technology.get("version"), str) or not technology.get("version", "").strip():
                errors.append("labeled_schema: technology.version mancante o non valida.")

    schema = labeled_schema.get("schema")
    if not isinstance(schema, dict):
        errors.append("labeled_schema: schema deve essere un oggetto.")
        return errors

    er_schema = {
        "format_version": labeled_schema.get("format_version"),
        "entities": schema.get("entities"),
        "relationships": schema.get("relationships")
    }

    er_errors = check_er_schema(er_schema)
    if er_errors:
        for error in er_errors:
            errors.append("schema: " + error)
        return errors

    entities = []
    relationships = {}

    for entity in er_schema["entities"]:
        entities.append(entity["name"])

    for relationship in er_schema["relationships"]:
        relationships[relationship["name"]] = relationship

    labeling = labeled_schema.get("labeling")
    if not isinstance(labeling, dict):
        errors.append("labeled_schema: labeling deve essere un oggetto.")
        return errors

    main_values = labeling.get("main_entities")
    if not isinstance(main_values, list) or len(main_values) == 0:
        errors.append("labeling: main_entities deve essere una lista non vuota.")
        main_values = []

    main_entities = []
    collections = {}

    for i in range(len(main_values)):
        value = main_values[i]
        current = f"main_entities[{i}]"

        if not isinstance(value, dict):
            errors.append(f"{current}: il valore deve essere un oggetto.")
            continue

        entity = value.get("entity")
        collection = value.get("collection")

        if entity not in entities:
            errors.append(f"{current}: entità '{entity}' non presente nello schema ER.")
            continue

        if entity in main_entities:
            errors.append(f"labeling: main entity '{entity}' duplicata.")
        else:
            main_entities.append(entity)

        if not isinstance(collection, str) or not collection.strip():
            errors.append(f"{current}: collection mancante o non valida.")
        elif collection != entity:
            errors.append(
                f"{current}: collection deve coincidere con il nome "
                f"della main entity '{entity}'."
            )
        else:
            collections[entity] = collection

    entity_labels = labeling.get("entity_labels")
    if not isinstance(entity_labels, list):
        errors.append("labeling: entity_labels deve essere una lista.")
        entity_labels = []

    labels = {}

    for i in range(len(entity_labels)):
        value = entity_labels[i]
        current = f"entity_labels[{i}]"

        if not isinstance(value, dict):
            errors.append(f"{current}: il valore deve essere un oggetto.")
            continue

        entity = value.get("entity")
        label = value.get("label")

        if entity not in entities:
            errors.append(f"{current}: entità '{entity}' non presente nello schema ER.")
            continue

        if entity in labels:
            errors.append(f"labeling: etichetta duplicata per l'entità '{entity}'.")
            continue

        if not isinstance(label, str) or not label.strip():
            errors.append(f"{current}: label mancante o non valida.")
            continue

        labels[entity] = label

    for entity in entities:
        if entity not in labels:
            errors.append(f"labeling: manca l'etichetta dell'entità '{entity}'.")

    for entity in main_entities:
        if entity in labels and entity in collections and labels[entity] != collections[entity]:
            errors.append(f"labeling: l'etichetta della main entity '{entity}' deve coincidere con la collection.")

    encapsulations = labeling.get("encapsulations")
    if not isinstance(encapsulations, list):
        errors.append("labeling: encapsulations deve essere una lista.")
        encapsulations = []

    parents = {}
    parent_relationships = {}
    represented = {}

    for relationship in relationships:
        represented[relationship] = {
            "encapsulation": 0,
            "references": []
        }

    for i in range(len(encapsulations)):
        value = encapsulations[i]
        current = f"encapsulations[{i}]"

        if not isinstance(value, dict):
            errors.append(f"{current}: il valore deve essere un oggetto.")
            continue

        relationship_name = value.get("relationship")
        entity = value.get("entity")
        into = value.get("into")

        if not isinstance(relationship_name, str):
            errors.append(f"{current}: relationship deve essere una stringa.")
            continue

        if relationship_name not in relationships:
            errors.append(f"{current}: relazione '{relationship_name}' non presente nello schema ER.")
            continue

        if entity not in entities or into not in entities:
            errors.append(f"{current}: entity oppure into non presente nello schema ER.")
            continue

        relationship = relationships[relationship_name]
        first = relationship["sides"][0]["entity"]
        second = relationship["sides"][1]["entity"]

        if first == second:
            errors.append(f"{current}: una self-relationship non può essere usata per un incapsulamento.")
            continue

        if not ((entity == first and into == second) or (entity == second and into == first)):
            errors.append(f"{current}: '{relationship_name}' non collega '{entity}' a '{into}'.")
            continue

        if entity in main_entities:
            errors.append(f"{current}: una main entity non può essere incapsulata.")

        if entity in parents:
            errors.append(f"labeling: l'entità '{entity}' ha più di un incapsulamento uscente.")
        else:
            parents[entity] = into
            parent_relationships[entity] = relationship_name

        represented[relationship_name]["encapsulation"] += 1

    for entity in entities:
        if entity in main_entities:
            continue
        if entity not in parents:
            errors.append(f"labeling: l'entità non-main '{entity}' deve avere un incapsulamento uscente.")

    depths = {}

    for entity in entities:
        if entity in main_entities:
            depths[entity] = 0
            continue

        current = entity
        visited = []
        depth = 0

        while current not in main_entities:
            if current in visited:
                errors.append(f"labeling: ciclo di incapsulamento che coinvolge '{current}'.")
                depth = None
                break

            visited.append(current)

            if current not in parents:
                depth = None
                break

            current = parents[current]
            depth += 1

        if depth is not None:
            depths[entity] = depth

    max_depth = 0
    for entity in depths:
        if depths[entity] > max_depth:
            max_depth = depths[entity]

    for depth in range(1, max_depth + 1):
        for entity in entities:
            if depths.get(entity) != depth or entity not in labels:
                continue

            parent = parents[entity]
            relationship = relationships[parent_relationships[entity]]
            cardinality = None

            for side in relationship["sides"]:
                if side["entity"] == entity:
                    cardinality = side["cardinality"]
                    break

            if cardinality is None:
                continue

            if cardinality["max"] == 1:
                if cardinality["min"] == 0:
                    expected = "XL"
                else:
                    expected = "X"
            else:
                if cardinality["min"] == 0:
                    expected = "XRL"
                else:
                    expected = "XR"

            if parent not in main_entities and cardinality["min"] == 1 and cardinality["max"] == 1:
                expected = labels.get(parent)

            if labels[entity] != expected:
                errors.append(f"labeling: l'etichetta di '{entity}' dovrebbe essere '{expected}'.")

    references = labeling.get("references")
    if not isinstance(references, list):
        errors.append("labeling: references deve essere una lista.")
        references = []

    for i in range(len(references)):
        value = references[i]
        current = f"references[{i}]"

        if not isinstance(value, dict):
            errors.append(f"{current}: il valore deve essere un oggetto.")
            continue

        relationship_name = value.get("relationship")
        stored_in = value.get("stored_in")
        target = value.get("target")
        label = value.get("label")

        if not isinstance(relationship_name, str):
            errors.append(f"{current}: relationship deve essere una stringa.")
            continue

        if relationship_name not in relationships:
            errors.append(f"{current}: relazione '{relationship_name}' non presente nello schema ER.")
            continue

        if stored_in not in entities or target not in entities:
            errors.append(f"{current}: stored_in oppure target non presente nello schema ER.")
            continue

        relationship = relationships[relationship_name]
        first = relationship["sides"][0]["entity"]
        second = relationship["sides"][1]["entity"]

        if not ((stored_in == first and target == second) or (stored_in == second and target == first)):
            errors.append(f"{current}: '{relationship_name}' non collega '{stored_in}' a '{target}'.")
            continue

        expected = "key"
        if target in main_entities:
            expected = "id"

        if label != expected:
            errors.append(f"{current}: label dovrebbe essere '{expected}'.")

        if first == second:
            stored_role = value.get("stored_role")
            target_role = value.get("target_role")
            first_role = relationship["sides"][0].get("role")
            second_role = relationship["sides"][1].get("role")

            valid_roles = False
            if stored_role == first_role and target_role == second_role:
                valid_roles = True
            if stored_role == second_role and target_role == first_role:
                valid_roles = True

            if not valid_roles:
                errors.append(f"{current}: stored_role e target_role non identificano i due lati della self-relationship.")

        direction = (stored_in, target, value.get("stored_role"), value.get("target_role"))
        if direction in represented[relationship_name]["references"]:
            errors.append(f"{current}: riferimento duplicato.")
        else:
            represented[relationship_name]["references"].append(direction)

    for relationship_name in represented:
        encapsulation_count = represented[relationship_name]["encapsulation"]
        reference_count = len(represented[relationship_name]["references"])

        if encapsulation_count > 1:
            errors.append(f"labeling: la relazione '{relationship_name}' è usata da più incapsulamenti.")

        if encapsulation_count > 0 and reference_count > 0:
            errors.append(f"labeling: la relazione '{relationship_name}' è rappresentata sia con incapsulamento sia con riferimento.")

        if encapsulation_count == 0 and reference_count == 0:
            errors.append(f"labeling: la relazione '{relationship_name}' non è rappresentata.")

        if reference_count > 2:
            errors.append(f"labeling: la relazione '{relationship_name}' contiene troppi riferimenti.")

        if reference_count == 2:
            first = represented[relationship_name]["references"][0]
            second = represented[relationship_name]["references"][1]

            relationship = relationships[relationship_name]
            self_relationship = relationship["sides"][0]["entity"] == relationship["sides"][1]["entity"]

            if self_relationship:
                if first[2] != second[3] or first[3] != second[2]:
                    errors.append(f"labeling: i due riferimenti di '{relationship_name}' non sono direzioni opposte.")
            else:
                if first[0] != second[1] or first[1] != second[0]:
                    errors.append(f"labeling: i due riferimenti di '{relationship_name}' non sono direzioni opposte.")

    partition = labeled_schema.get("partition")
    if not isinstance(partition, list) or len(partition) == 0:
        errors.append("labeled_schema: partition deve essere una lista non vuota.")
        partition = []

    seen_main = []
    seen_entities = []

    for i in range(len(partition)):
        block = partition[i]
        current = f"partition[{i}]"

        if not isinstance(block, dict):
            errors.append(f"{current}: il blocco deve essere un oggetto.")
            continue

        main_entity = block.get("main_entity")
        collection = block.get("collection")
        block_entities = block.get("entities")
        block_relationships = block.get("encapsulation_relationships")

        if main_entity not in main_entities:
            errors.append(f"{current}: main_entity '{main_entity}' non presente tra le main entity.")
            continue

        if main_entity in seen_main:
            errors.append(f"partition: main_entity '{main_entity}' duplicata.")
        else:
            seen_main.append(main_entity)

        if main_entity in collections and collection != collections[main_entity]:
            errors.append(f"{current}: collection non coerente con la main entity '{main_entity}'.")

        if not isinstance(block_entities, list) or len(block_entities) == 0:
            errors.append(f"{current}: entities deve essere una lista non vuota.")
            block_entities = []

        for entity in block_entities:
            if not isinstance(entity, str):
                errors.append(f"{current}: entities deve contenere nomi di entità.")
                continue

            if entity not in entities:
                errors.append(f"{current}: entità '{entity}' non presente nello schema ER.")
            elif entity in seen_entities:
                errors.append(f"partition: entità '{entity}' presente in più blocchi.")
            else:
                seen_entities.append(entity)

        if not isinstance(block_relationships, list):
            errors.append(f"{current}: encapsulation_relationships deve essere una lista.")
            block_relationships = []
            
        for relationship in block_relationships:
            if not isinstance(relationship, str):
                errors.append(f"{current}: encapsulation_relationships deve contenere nomi di relazioni.")

        expected_entities = []
        expected_relationships = []

        for entity in entities:
            if entity not in depths:
                continue

            root = entity
            while root not in main_entities:
                root = parents[root]

            if root == main_entity:
                expected_entities.append(entity)
                if entity in parent_relationships:
                    expected_relationships.append(parent_relationships[entity])

        valid_block_entities = []
        for entity in block_entities:
            if isinstance(entity, str):
                valid_block_entities.append(entity)

        if set(valid_block_entities) != set(expected_entities):
            errors.append(f"{current}: entities non coerente con gli incapsulamenti.")

        valid_block_relationships = []
        for relationship in block_relationships:
            if isinstance(relationship, str):
                valid_block_relationships.append(relationship)

        if set(valid_block_relationships) != set(expected_relationships):
            errors.append(f"{current}: encapsulation_relationships non coerente con gli incapsulamenti.")

    for entity in main_entities:
        if entity not in seen_main:
            errors.append(f"partition: manca il blocco della main entity '{entity}'.")

    for entity in entities:
        if entity not in seen_entities:
            errors.append(f"partition: manca l'entità '{entity}'.")

    return errors


def check_size_values(values, where, errors):
    if not isinstance(values, dict):
        errors.append(f"{where}: le statistiche devono essere un oggetto.")
        return

    avg_size = values.get("avg_size_bytes")
    max_size = values.get("max_size_bytes")

    if "avg_size_bytes" in values and (not is_number(avg_size) or avg_size < 0):
        errors.append(f"{where}: avg_size_bytes non valido.")

    if "max_size_bytes" in values and (not is_number(max_size) or max_size < 0):
        errors.append(f"{where}: max_size_bytes non valido.")

    if is_number(avg_size) and is_number(max_size) and avg_size > max_size:
        errors.append(f"{where}: avg_size_bytes non può superare max_size_bytes.")

    if "avg_values" in values:
        avg_values = values["avg_values"]
        if not is_number(avg_values) or avg_values < 0:
            errors.append(f"{where}: avg_values non valido.")


def check_statistics(data_statistics, er_schema, entities, attributes, relationships, relationship_attributes, errors):
    if not isinstance(data_statistics, dict):
        errors.append("data_system: data_statistics deve essere un oggetto.")
        return

    entity_stats = data_statistics.get("entities")
    relationship_stats = data_statistics.get("relationships")

    if not isinstance(entity_stats, dict):
        errors.append("data_statistics: entities deve essere un oggetto.")
        entity_stats = {}

    if not isinstance(relationship_stats, dict):
        errors.append("data_statistics: relationships deve essere un oggetto.")
        relationship_stats = {}

    entity_definitions = {}
    relationship_definitions = {}

    for entity in er_schema.get("entities", []):
        entity_definitions[entity["name"]] = {}
        for attribute in entity.get("attributes", []):
            entity_definitions[entity["name"]][attribute["name"]] = attribute

    for relationship in er_schema.get("relationships", []):
        relationship_definitions[relationship["name"]] = relationship

    for entity in entity_stats:
        if entity not in entities:
            errors.append(f"data_statistics: entità '{entity}' non presente nello schema ER.")
            continue

        stats = entity_stats[entity]
        if not isinstance(stats, dict):
            errors.append(f"Statistiche di '{entity}': il valore deve essere un oggetto.")
            continue

        if "instances" in stats:
            value = stats["instances"]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"Statistiche di '{entity}': instances non valido.")

        if "new_instances_per_time_unit" in stats:
            value = stats["new_instances_per_time_unit"]
            if not is_number(value) or value < 0:
                errors.append(f"Statistiche di '{entity}': new_instances_per_time_unit non valido.")

        if "working_set_fraction" in stats:
            value = stats["working_set_fraction"]
            if not is_number(value) or value < 0 or value > 1:
                errors.append(f"Statistiche di '{entity}': working_set_fraction deve essere compreso tra 0 e 1.")

        attr_stats = stats.get("attributes", {})
        if not isinstance(attr_stats, dict):
            errors.append(f"Statistiche di '{entity}': attributes deve essere un oggetto.")
            continue

        for attribute in attr_stats:
            if attribute not in attributes.get(entity, []):
                errors.append(f"Statistiche di '{entity}': attributo '{attribute}' non presente nello schema ER.")
            else:
                current = f"Statistiche di '{entity}.{attribute}'"
                check_size_values(attr_stats[attribute], current, errors)

                values = attr_stats[attribute]
                definition = entity_definitions.get(entity, {}).get(attribute)
                if isinstance(values, dict) and definition is not None and "avg_values" in values:
                    avg_values = values["avg_values"]
                    cardinality = definition["cardinality"]

                    if is_number(avg_values):
                        minimum = cardinality["min"]
                        maximum = cardinality["max"]

                        if avg_values < minimum:
                            errors.append(f"{current}: avg_values non può essere inferiore alla cardinalità minima {minimum}.")

                        if maximum != "N" and avg_values > maximum:
                            errors.append(f"{current}: avg_values non può superare la cardinalità massima {maximum}.")

    for relationship in relationship_stats:
        if relationship not in relationships:
            errors.append(f"data_statistics: relazione '{relationship}' non presente nello schema ER.")
            continue

        stats = relationship_stats[relationship]
        if not isinstance(stats, dict):
            errors.append(f"Statistiche di '{relationship}': il valore deve essere un oggetto.")
            continue

        sides = stats.get("sides")
        if not isinstance(sides, list) or len(sides) != 2:
            errors.append(f"Statistiche di '{relationship}': sides deve contenere due lati.")
            sides = []

        seen = []
        for i in range(len(sides)):
            side = sides[i]
            current = f"Statistiche di '{relationship}'.sides[{i}]"

            if not isinstance(side, dict):
                errors.append(f"{current}: il lato deve essere un oggetto.")
                continue

            entity = side.get("entity")
            if entity not in relationships[relationship]:
                errors.append(f"{current}: entità '{entity}' non collegata dalla relazione.")
            elif relationships[relationship][0] != relationships[relationship][1] and entity in seen:
                errors.append(f"{current}: entità '{entity}' ripetuta nei lati.")
            else:
                seen.append(entity)

            for name in ["avg_connected", "growth_per_time_unit", "future_avg_connected"]:
                if name in side:
                    value = side[name]
                    if not is_number(value) or value < 0:
                        errors.append(f"{current}: {name} non valido.")

            for name in ["max_connected", "cardinality_limit"]:
                if name in side:
                    value = side[name]
                    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                        errors.append(f"{current}: {name} deve essere un intero non negativo.")

            avg_connected = side.get("avg_connected")
            future_avg = side.get("future_avg_connected")
            max_connected = side.get("max_connected")
            cardinality_limit = side.get("cardinality_limit")
            valid_avg = is_number(avg_connected)
            valid_future = is_number(future_avg)
            valid_max = isinstance(max_connected, int) and not isinstance(max_connected, bool)
            valid_limit = isinstance(cardinality_limit, int) and not isinstance(cardinality_limit, bool)

            if valid_avg and valid_max and avg_connected > max_connected:
                errors.append(f"{current}: avg_connected non può superare max_connected.")

            if valid_max and valid_limit and max_connected > cardinality_limit:
                errors.append(f"{current}: max_connected non può superare cardinality_limit.")

            definition = relationship_definitions.get(relationship)
            er_cardinality = None

            if definition is not None and definition["sides"][0]["entity"] != definition["sides"][1]["entity"]:
                for er_side in definition["sides"]:
                    if er_side["entity"] == entity:
                        er_cardinality = er_side["cardinality"]
                        break

            if er_cardinality is not None:
                minimum = er_cardinality["min"]
                maximum = er_cardinality["max"]

                if valid_limit and cardinality_limit < minimum:
                    errors.append(f"{current}: cardinality_limit non può essere inferiore alla cardinalità minima {minimum}.")

                for name, value, valid in [
                    ("avg_connected", avg_connected, valid_avg),
                    ("max_connected", max_connected, valid_max),
                    ("future_avg_connected", future_avg, valid_future)
                ]:
                    if not valid:
                        continue

                    if value < minimum:
                        errors.append(f"{current}: {name} non può essere inferiore alla cardinalità minima {minimum}.")

                    if maximum != "N" and value > maximum:
                        errors.append(f"{current}: {name} non può superare la cardinalità massima {maximum}.")

                    if valid_limit and value > cardinality_limit:
                        errors.append(f"{current}: {name} non può superare cardinality_limit.")

        attr_stats = stats.get("attributes", {})
        if not isinstance(attr_stats, dict):
            errors.append(f"Statistiche di '{relationship}': attributes deve essere un oggetto.")
        else:
            for attribute in attr_stats:
                if attribute not in relationship_attributes.get(relationship, []):
                    errors.append(f"Statistiche di '{relationship}': attributo '{attribute}' non presente nello schema ER.")
                else:
                    current = f"Statistiche di '{relationship}.{attribute}'"
                    check_size_values(attr_stats[attribute], current, errors)

                    values = attr_stats[attribute]
                    definition = relationship_definitions.get(relationship)
                    attribute_definition = None

                    if definition is not None:
                        for item in definition.get("attributes", []):
                            if item["name"] == attribute:
                                attribute_definition = item
                                break

                    if isinstance(values, dict) and attribute_definition is not None and "avg_values" in values:
                        avg_values = values["avg_values"]
                        cardinality = attribute_definition["cardinality"]

                        if is_number(avg_values):
                            minimum = cardinality["min"]
                            maximum = cardinality["max"]

                            if avg_values < minimum:
                                errors.append(f"{current}: avg_values non può essere inferiore alla cardinalità minima {minimum}.")

                            if maximum != "N" and avg_values > maximum:
                                errors.append(f"{current}: avg_values non può superare la cardinalità massima {maximum}.")

    path_statistics = data_statistics.get("path_statistics", [])
    if not isinstance(path_statistics, list):
        errors.append("data_statistics: path_statistics deve essere una lista.")
        return

    for i in range(len(path_statistics)):
        path = path_statistics[i]
        current = f"path_statistics[{i}]"

        if not isinstance(path, dict):
            errors.append(f"{current}: la statistica deve essere un oggetto.")
            continue

        start = path.get("from")
        end = path.get("to")
        path_relationships = path.get("relationships")

        if start not in entities or end not in entities:
            errors.append(f"{current}: from oppure to non presente nello schema ER.")

        if not isinstance(path_relationships, list) or len(path_relationships) == 0:
            errors.append(f"{current}: relationships deve essere una lista non vuota.")
        elif start in entities:
            current_entity = start
            for relationship in path_relationships:
                if not isinstance(relationship, str):
                    errors.append(f"{current}: relationships deve contenere nomi di relazioni.")
                    break

                if relationship not in relationships or current_entity not in relationships[relationship]:
                    errors.append(f"{current}: il percorso non è coerente con lo schema ER.")
                    break

                sides = relationships[relationship]
                if sides[0] == current_entity:
                    current_entity = sides[1]
                else:
                    current_entity = sides[0]

            if current_entity != end:
                errors.append(f"{current}: il percorso non termina in '{end}'.")

        if "avg_distinct_targets" in path:
            value = path["avg_distinct_targets"]
            if not is_number(value) or value < 0:
                errors.append(f"{current}: avg_distinct_targets non valido.")

        probabilities = []
        for name in ["probability_zero_targets", "probability_one_target", "probability_multiple_targets"]:
            if name in path:
                value = path[name]
                if not is_number(value) or value < 0 or value > 1:
                    errors.append(f"{current}: {name} deve essere compreso tra 0 e 1.")
                else:
                    probabilities.append(value)

        if len(probabilities) == 3 and abs(sum(probabilities) - 1) > 0.000001:
            errors.append(f"{current}: le tre probabilità devono avere somma 1.")


def check_indexes(indexes, entities, attributes, errors):
    if not isinstance(indexes, list):
        errors.append("data_system: indexes deve essere una lista.")
        return []

    names = []

    for i in range(len(indexes)):
        index = indexes[i]
        current = f"indexes[{i}]"

        if not isinstance(index, dict):
            errors.append(f"{current}: l'indice deve essere un oggetto.")
            continue

        name = index.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{current}: name mancante o non valido.")
        elif name in names:
            errors.append(f"indexes: indice '{name}' duplicato.")
        else:
            names.append(name)

        fields = index.get("fields")
        if not isinstance(fields, list) or len(fields) == 0:
            errors.append(f"{current}: fields deve essere una lista non vuota.")
            fields = []

        for j in range(len(fields)):
            field = fields[j]
            field_where = f"{current}.fields[{j}]"

            if not isinstance(field, dict):
                errors.append(f"{field_where}: il dato deve essere un oggetto.")
                continue

            entity = field.get("entity")
            attribute = field.get("attribute")
            if entity not in entities:
                errors.append(f"{field_where}: entità '{entity}' non presente nello schema ER.")
            elif attribute not in attributes.get(entity, []):
                errors.append(f"{field_where}: attributo '{attribute}' non presente in '{entity}'.")

        if "participation_fraction" in index:
            value = index["participation_fraction"]
            if not is_number(value) or value < 0 or value > 1:
                errors.append(f"{current}: participation_fraction deve essere compreso tra 0 e 1.")

        for name in ["avg_entry_memory_bytes", "avg_entry_storage_bytes"]:
            if name in index:
                value = index[name]
                if not is_number(value) or value < 0:
                    errors.append(f"{current}: {name} non valido.")

    return names


def check_queries(query_workload, entities, attributes, relationships, index_names, errors):
    if not isinstance(query_workload, dict):
        errors.append("data_system: query_workload deve essere un oggetto.")
        return

    if query_workload.get("frequency_type") not in ["absolute", "weight"]:
        errors.append("query_workload: frequency_type deve essere 'absolute' oppure 'weight'.")

    queries = query_workload.get("queries")
    if not isinstance(queries, list):
        errors.append("query_workload: queries deve essere una lista.")
        return

    names = []

    for i in range(len(queries)):
        query = queries[i]
        current = f"queries[{i}]"

        if not isinstance(query, dict):
            errors.append(f"{current}: la query deve essere un oggetto.")
            continue

        name = query.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{current}: name mancante o non valido.")
        elif name in names:
            errors.append(f"query_workload: query '{name}' duplicata.")
        else:
            names.append(name)

        frequency = query.get("frequency")
        if not is_number(frequency) or frequency < 0:
            errors.append(f"{current}: frequency deve essere un numero non negativo.")

        target = query.get("target_entity")
        if target not in entities:
            errors.append(f"{current}: target_entity '{target}' non presente nello schema ER.")
            continue

        entities_in_selection = []
        entities_in_projection = []

        selection_paths = query.get("selection_paths")
        if not isinstance(selection_paths, list) or len(selection_paths) == 0:
            errors.append(f"{current}: selection_paths deve essere una lista non vuota.")
            selection_paths = []

        for j in range(len(selection_paths)):
            check_path(selection_paths[j], target, entities, relationships, f"{current}.selection_paths[{j}]", errors)
            if not isinstance(selection_paths[j], list):
                continue
            for step in selection_paths[j]:
                if isinstance(step, dict) and step.get("entity") in entities:
                    entities_in_selection.append(step["entity"])

        projection_paths = query.get("projection_paths")
        if not isinstance(projection_paths, list) or len(projection_paths) == 0:
            errors.append(f"{current}: projection_paths deve essere una lista non vuota.")
            projection_paths = []

        for j in range(len(projection_paths)):
            check_path(projection_paths[j], target, entities, relationships, f"{current}.projection_paths[{j}]", errors)
            if not isinstance(projection_paths[j], list):
                continue
            for step in projection_paths[j]:
                if isinstance(step, dict) and step.get("entity") in entities:
                    entities_in_projection.append(step["entity"])

        predicates = query.get("predicates", [])
        if not isinstance(predicates, list):
            errors.append(f"{current}: predicates deve essere una lista.")
            predicates = []

        for j in range(len(predicates)):
            predicate = predicates[j]
            predicate_where = f"{current}.predicates[{j}]"

            if not isinstance(predicate, dict):
                errors.append(f"{predicate_where}: il predicato deve essere un oggetto.")
                continue

            entity = predicate.get("entity")
            attribute = predicate.get("attribute")

            if entity not in entities:
                errors.append(f"{predicate_where}: entità '{entity}' non presente nello schema ER.")
            elif attribute not in attributes.get(entity, []):
                errors.append(f"{predicate_where}: attributo '{attribute}' non presente in '{entity}'.")
            elif entity not in entities_in_selection:
                errors.append(f"{predicate_where}: l'entità '{entity}' non compare nei selection_paths.")

            if not isinstance(predicate.get("operator"), str) or not predicate.get("operator", "").strip():
                errors.append(f"{predicate_where}: operator mancante o non valido.")

            for field in ["selectivity", "post_index_selectivity"]:
                if field in predicate:
                    value = predicate[field]
                    if not is_number(value) or value < 0 or value > 1:
                        errors.append(f"{predicate_where}: {field} deve essere compreso tra 0 e 1.")

            if "index" in predicate and predicate["index"] not in index_names:
                errors.append(f"{predicate_where}: indice '{predicate['index']}' non definito.")

        projection_attributes = query.get("projection_attributes", [])
        if not isinstance(projection_attributes, list):
            errors.append(f"{current}: projection_attributes deve essere una lista.")
            projection_attributes = []

        for j in range(len(projection_attributes)):
            field = projection_attributes[j]
            field_where = f"{current}.projection_attributes[{j}]"

            if not isinstance(field, dict):
                errors.append(f"{field_where}: il dato deve essere un oggetto.")
                continue

            entity = field.get("entity")
            attribute = field.get("attribute")

            if entity not in entities:
                errors.append(f"{field_where}: entità '{entity}' non presente nello schema ER.")
            elif attribute not in attributes.get(entity, []):
                errors.append(f"{field_where}: attributo '{attribute}' non presente in '{entity}'.")
            elif entity not in entities_in_projection:
                errors.append(f"{field_where}: l'entità '{entity}' non compare nei projection_paths.")

        for field in ["estimated_result_cardinality", "estimated_avg_result_size_bytes"]:
            if field in query:
                value = query[field]
                if not is_number(value) or value < 0:
                    errors.append(f"{current}: {field} non valido.")

        temporary_operations = query.get("temporary_operations", [])
        if not isinstance(temporary_operations, list):
            errors.append(f"{current}: temporary_operations deve essere una lista.")
            temporary_operations = []

        for j in range(len(temporary_operations)):
            operation = temporary_operations[j]
            op_where = f"{current}.temporary_operations[{j}]"

            if not isinstance(operation, dict):
                errors.append(f"{op_where}: l'operazione deve essere un oggetto.")
                continue

            if not isinstance(operation.get("type"), str) or not operation.get("type", "").strip():
                errors.append(f"{op_where}: type mancante o non valido.")

            if operation.get("after_entity") not in entities:
                errors.append(f"{op_where}: after_entity non presente nello schema ER.")

            for field in ["items_kept", "avg_item_size_bytes"]:
                if field in operation:
                    value = operation[field]
                    if not is_number(value) or value < 0:
                        errors.append(f"{op_where}: {field} non valido.")


def check_updates(update_workload, entities, attributes, relationships, errors):
    if not isinstance(update_workload, dict):
        errors.append("data_system: update_workload deve essere un oggetto.")
        return

    if update_workload.get("frequency_type") not in ["absolute", "weight"]:
        errors.append("update_workload: frequency_type deve essere 'absolute' oppure 'weight'.")

    updates = update_workload.get("updates")
    if not isinstance(updates, list):
        errors.append("update_workload: updates deve essere una lista.")
        return

    names = []

    for i in range(len(updates)):
        update = updates[i]
        current = f"updates[{i}]"

        if not isinstance(update, dict):
            errors.append(f"{current}: l'update deve essere un oggetto.")
            continue

        name = update.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{current}: name mancante o non valido.")
        elif name in names:
            errors.append(f"update_workload: update '{name}' duplicato.")
        else:
            names.append(name)

        frequency = update.get("frequency")
        if not is_number(frequency) or frequency < 0:
            errors.append(f"{current}: frequency deve essere un numero non negativo.")

        operation = update.get("operation")
        if operation not in ["set_attribute", "add_relationship", "remove_relationship"]:
            errors.append(f"{current}: operation non valida.")

        if update.get("granularity") not in ["field", "subdocument", "document"]:
            errors.append(f"{current}: granularity non valida.")

        target = update.get("target")
        if not isinstance(target, dict):
            errors.append(f"{current}: target deve essere un oggetto.")
        elif operation == "set_attribute":
            entity = target.get("entity")
            attribute = target.get("attribute")
            if entity not in entities:
                errors.append(f"{current}: target.entity '{entity}' non presente nello schema ER.")
            elif attribute not in attributes.get(entity, []):
                errors.append(f"{current}: target.attribute '{attribute}' non presente in '{entity}'.")
        elif operation in ["add_relationship", "remove_relationship"]:
            relationship = target.get("relationship")

            if not isinstance(relationship, str):
                errors.append(f"{current}: target.relationship deve essere una stringa.")
            elif relationship not in relationships:
                errors.append(f"{current}: target.relationship '{relationship}' non presente nello schema ER.")

        if "avg_modified_size_bytes" in update:
            value = update["avg_modified_size_bytes"]
            if not is_number(value) or value < 0:
                errors.append(f"{current}: avg_modified_size_bytes non valido.")


def check_system(system, errors):
    if not isinstance(system, dict):
        errors.append("data_system: system deve essere un oggetto.")
        return

    technology = system.get("technology")
    if not isinstance(technology, dict):
        errors.append("system: technology deve essere un oggetto.")
    else:
        if technology.get("name") not in ["mongodb", "couchbase"]:
            errors.append("technology: name deve essere 'mongodb' oppure 'couchbase'.")
        if not isinstance(technology.get("version"), str) or not technology.get("version", "").strip():
            errors.append("technology: version mancante o non valida.")

    if "memory" in system:
        memory = system["memory"]
        if not isinstance(memory, dict):
            errors.append("system: memory deve essere un oggetto.")
        else:
            for name in ["data_available_bytes", "index_available_bytes"]:
                if name in memory and (not is_number(memory[name]) or memory[name] <= 0):
                    errors.append(f"memory: {name} deve essere maggiore di 0.")

    if "temporary_storage" in system:
        temporary = system["temporary_storage"]
        if not isinstance(temporary, dict):
            errors.append("system: temporary_storage deve essere un oggetto.")
        else:
            if "memory_limit_bytes" in temporary and (not is_number(temporary["memory_limit_bytes"]) or temporary["memory_limit_bytes"] <= 0):
                errors.append("temporary_storage: memory_limit_bytes deve essere maggiore di 0.")
            if "spill_allowed" in temporary and not isinstance(temporary["spill_allowed"], bool):
                errors.append("temporary_storage: spill_allowed deve essere booleano.")
            if "disk_limit_bytes" in temporary and (not is_number(temporary["disk_limit_bytes"]) or temporary["disk_limit_bytes"] < 0):
                errors.append("temporary_storage: disk_limit_bytes non valido.")

    if "replication" in system:
        replication = system["replication"]
        if not isinstance(replication, dict):
            errors.append("system: replication deve essere un oggetto.")
        else:
            for name in ["document_replicas", "index_replicas"]:
                if name in replication:
                    value = replication[name]
                    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                        errors.append(f"replication: {name} deve essere un intero non negativo.")

    if "distribution" in system:
        distribution = system["distribution"]
        if not isinstance(distribution, dict):
            errors.append("system: distribution deve essere un oggetto.")
        elif "nodes" in distribution:
            value = distribution["nodes"]
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                errors.append("distribution: nodes deve essere un intero maggiore o uguale a 1.")

    if "size_estimates" in system:
        size_estimates = system["size_estimates"]
        if not isinstance(size_estimates, dict):
            errors.append("system: size_estimates deve essere un oggetto.")
        else:
            for name in ["memory_ratio", "storage_ratio"]:
                if name in size_estimates and (not is_number(size_estimates[name]) or size_estimates[name] <= 0):
                    errors.append(f"size_estimates: {name} deve essere maggiore di 0.")


def check_data_system(data_system, er_schema):
    errors = []

    if not isinstance(data_system, dict):
        return ["Il file data_system deve contenere un oggetto JSON."]

    if data_system.get("format_version") != "1.0":
        errors.append("data_system: format_version deve essere '1.0'.")

    entities, attributes, relationships, relationship_attributes = er_data(er_schema)

    evaluation = data_system.get("evaluation")
    if not isinstance(evaluation, dict):
        errors.append("data_system: evaluation deve essere un oggetto.")
    else:
        if not isinstance(evaluation.get("time_unit"), str) or not evaluation.get("time_unit", "").strip():
            errors.append("evaluation: time_unit mancante o non valido.")

        if "planning_horizon" in evaluation:
            value = evaluation["planning_horizon"]
            if not is_number(value) or value < 0:
                errors.append("evaluation: planning_horizon deve essere non negativo.")

        if "query_cost_weights" in evaluation:
            weights = evaluation["query_cost_weights"]
            if not isinstance(weights, dict):
                errors.append("evaluation: query_cost_weights deve essere un oggetto.")
            else:
                for name in ["scan", "unwind", "lookup"]:
                    if name in weights and (not is_number(weights[name]) or weights[name] < 0):
                        errors.append(f"query_cost_weights: '{name}' deve essere non negativo.")

        if not isinstance(evaluation.get("allow_information_loss"), bool):
            errors.append("evaluation: allow_information_loss deve essere booleano.")

        if "lifecycle_scenario" in evaluation and evaluation["lifecycle_scenario"] not in ["create", "migration"]:
            errors.append("evaluation: lifecycle_scenario deve essere 'create' oppure 'migration'.")

    check_statistics(data_system.get("data_statistics"), er_schema, entities, attributes, relationships, relationship_attributes, errors)

    index_names = check_indexes(data_system.get("indexes"), entities, attributes, errors)
    check_queries(data_system.get("query_workload"), entities, attributes, relationships, index_names, errors)
    check_updates(data_system.get("update_workload"), entities, attributes, relationships, errors)
    check_system(data_system.get("system"), errors)

    if "migration" in data_system:
        migration = data_system["migration"]
        if not isinstance(migration, dict):
            errors.append("data_system: migration deve essere un oggetto.")
        else:
            if migration.get("mode") != "full_rebuild":
                errors.append("migration: mode deve essere 'full_rebuild'.")

            sources = migration.get("source_structures")
            if not isinstance(sources, list):
                errors.append("migration: source_structures deve essere una lista.")
                sources = []

            names = []
            for i in range(len(sources)):
                source = sources[i]
                current = f"source_structures[{i}]"

                if not isinstance(source, dict):
                    errors.append(f"{current}: la struttura deve essere un oggetto.")
                    continue

                name = source.get("name")
                if not isinstance(name, str) or not name.strip():
                    errors.append(f"{current}: name mancante o non valido.")
                elif name in names:
                    errors.append(f"migration: source_structure '{name}' duplicata.")
                else:
                    names.append(name)

                instances = source.get("instances")
                if not isinstance(instances, int) or isinstance(instances, bool) or instances < 0:
                    errors.append(f"{current}: instances deve essere un intero non negativo.")

                avg_size = source.get("avg_size_bytes")
                if not is_number(avg_size) or avg_size < 0:
                    errors.append(f"{current}: avg_size_bytes non valido.")

                maps_to = source.get("maps_to")
                if not isinstance(maps_to, list) or len(maps_to) == 0:
                    errors.append(f"{current}: maps_to deve essere una lista non vuota.")
                else:
                    for entity in maps_to:
                        if entity not in entities:
                            errors.append(f"{current}: maps_to contiene l'entità sconosciuta '{entity}'.")

    return errors


def check_labeled_technology(labeled_schema, data_system):
    errors = []

    technology = labeled_schema.get("technology")
    if technology is None:
        return errors

    if not isinstance(technology, dict):
        return errors

    system = data_system.get("system", {})
    current = system.get("technology", {})

    if not isinstance(current, dict):
        return errors

    if technology.get("name") != current.get("name"):
        errors.append("technology: il nome nel labeled_schema non coincide con quello nel data_system.")

    if technology.get("version") != current.get("version"):
        errors.append("technology: la versione nel labeled_schema non coincide con quella nel data_system.")

    return errors


def need_instances(er_schema, entity_stats, metric, errors):
    for entity in er_schema.get("entities", []):
        name = entity["name"]
        if name not in entity_stats or "instances" not in entity_stats[name]:
            errors.append(f"Metrica {metric}: manca instances per '{name}'.")


def need_rel_avg(er_schema, relationship_stats, metric, errors):
    for relationship in er_schema.get("relationships", []):
        name = relationship["name"]
        sides = relationship_stats.get(name, {}).get("sides", [])

        if len(sides) != 2:
            errors.append(f"Metrica {metric}: mancano le cardinalità medie per '{name}'.")
            continue

        for side in sides:
            if "avg_connected" not in side:
                errors.append(f"Metrica {metric}: manca avg_connected per un lato di '{name}'.")


def need_sizes(er_schema, entity_stats, relationship_stats, metric, size_name, errors):
    for entity in er_schema.get("entities", []):
        entity_name = entity["name"]
        stats = entity_stats.get(entity_name, {}).get("attributes", {})

        for attribute in entity.get("attributes", []):
            attribute_name = attribute["name"]
            if attribute_name not in stats or size_name not in stats[attribute_name]:
                errors.append(f"Metrica {metric}: manca {size_name} per '{entity_name}.{attribute_name}'.")

            if size_name == "avg_size_bytes":
                cardinality = attribute["cardinality"]
                if cardinality["max"] != 1 and cardinality["min"] != cardinality["max"]:
                    if "avg_values" not in stats.get(attribute_name, {}):
                        errors.append(f"Metrica {metric}: manca avg_values per '{entity_name}.{attribute_name}'.")

    for relationship in er_schema.get("relationships", []):
        relationship_name = relationship["name"]
        stats = relationship_stats.get(relationship_name, {}).get("attributes", {})

        for attribute in relationship.get("attributes", []):
            attribute_name = attribute["name"]
            if attribute_name not in stats or size_name not in stats[attribute_name]:
                errors.append(f"Metrica {metric}: manca {size_name} per '{relationship_name}.{attribute_name}'.")

            if size_name == "avg_size_bytes":
                cardinality = attribute["cardinality"]
                if cardinality["max"] != 1 and cardinality["min"] != cardinality["max"]:
                    if "avg_values" not in stats.get(attribute_name, {}):
                        errors.append(f"Metrica {metric}: manca avg_values per '{relationship_name}.{attribute_name}'.")


def need_index_avg_values(er_schema, entity_stats, indexes, metric, errors):
    definitions = {}

    for entity in er_schema.get("entities", []):
        attributes = {}
        for attribute in entity.get("attributes", []):
            attributes[attribute["name"]] = attribute
        definitions[entity["name"]] = attributes

    for index in indexes:
        for field in index.get("fields", []):
            entity_name = field.get("entity")
            attribute_name = field.get("attribute")
            attribute = definitions.get(entity_name, {}).get(attribute_name)

            if attribute is None:
                continue

            cardinality = attribute["cardinality"]
            if cardinality["max"] == 1 or cardinality["min"] == cardinality["max"]:
                continue

            statistics = entity_stats.get(entity_name, {}).get("attributes", {}).get(attribute_name, {})
            if "avg_values" not in statistics:
                errors.append(f"Metrica {metric}: manca avg_values per '{entity_name}.{attribute_name}'.")


def frequency_sum(operations):
    total = 0
    for operation in operations:
        value = operation.get("frequency", 0)
        if is_number(value):
            total += value
    return total


def check_metric_data(er_schema, data_system, selected_metrics):
    errors = []

    statistics = data_system.get("data_statistics", {})
    entity_stats = statistics.get("entities", {})
    relationship_stats = statistics.get("relationships", {})
    queries = data_system.get("query_workload", {}).get("queries", [])
    updates = data_system.get("update_workload", {}).get("updates", [])
    indexes = data_system.get("indexes", [])
    system = data_system.get("system", {})
    evaluation = data_system.get("evaluation", {})

    for metric in selected_metrics:
        if metric in [1, 2, 3, 4, 5] and len(queries) == 0:
            errors.append(f"Metrica {metric}: il query workload è vuoto.")

        if metric in [14, 15, 16] and len(updates) == 0:
            errors.append(f"Metrica {metric}: l'update workload è vuoto.")

        if metric in [3, 4, 5, 6, 12, 17]:
            need_instances(er_schema, entity_stats, metric, errors)

        if metric in [3, 4, 5, 6, 10, 12, 13, 14, 15, 17]:
            need_rel_avg(er_schema, relationship_stats, metric, errors)

        if metric == 7 and len(indexes) > 0:
            need_instances(er_schema, entity_stats, 7, errors)
            need_rel_avg(er_schema, relationship_stats, 7, errors)

        if metric == 11:
            nodes = system.get("distribution", {}).get("nodes")
            if nodes is not None and nodes > 1:
                if len(queries) == 0:
                    errors.append("Metrica 11: il query workload è vuoto.")
                need_instances(er_schema, entity_stats, 11, errors)
                need_rel_avg(er_schema, relationship_stats, 11, errors)

        if metric in [1, 2]:
            weights = evaluation.get("query_cost_weights", {})
            for name in ["scan", "unwind", "lookup"]:
                if name not in weights:
                    errors.append(f"Metrica {metric}: manca il peso '{name}'.")

            if metric == 2 and frequency_sum(queries) <= 0:
                errors.append("Metrica 2: la somma delle frequenze delle query deve essere maggiore di 0.")

        elif metric in [3, 4, 5]:
            if frequency_sum(queries) <= 0:
                errors.append(
                    f"Metrica {metric}: la somma delle frequenze "
                    "delle query deve essere maggiore di 0."
                )

            for query in queries:
                if query.get("frequency", 0) <= 0:
                    continue

                for predicate in query.get("predicates", []):
                    if "selectivity" not in predicate:
                        errors.append(f"Metrica {metric}: manca selectivity nella query '{query.get('name')}'.")

            if metric == 4:
                need_sizes(er_schema, entity_stats, relationship_stats, 4, "avg_size_bytes", errors)

        elif metric == 6:
            need_sizes(er_schema, entity_stats, relationship_stats, 6, "avg_size_bytes", errors)

            for entity in er_schema.get("entities", []):
                name = entity["name"]
                if "working_set_fraction" not in entity_stats.get(name, {}):
                    errors.append(f"Metrica 6: manca working_set_fraction per '{name}'.")

            if "data_available_bytes" not in system.get("memory", {}):
                errors.append("Metrica 6: manca system.memory.data_available_bytes.")
            if "memory_ratio" not in system.get("size_estimates", {}):
                errors.append("Metrica 6: manca system.size_estimates.memory_ratio.")

        elif metric == 7:
            if len(indexes) > 0:
                need_index_avg_values(er_schema, entity_stats, indexes, 7, errors)

                for index in indexes:
                    if "participation_fraction" not in index:
                        errors.append(f"Metrica 7: manca participation_fraction per '{index.get('name')}'.")
                    if "avg_entry_memory_bytes" not in index:
                        errors.append(f"Metrica 7: manca avg_entry_memory_bytes per '{index.get('name')}'.")

                if "index_available_bytes" not in system.get("memory", {}):
                    errors.append("Metrica 7: manca system.memory.index_available_bytes.")

        elif metric == 8:
            has_temporary = False
            need_phase_data = False
            need_average_sizes = False

            for query in queries:
                if query.get("frequency", 0) <= 0:
                    continue

                operations = query.get("temporary_operations", [])
                if len(operations) > 0:
                    has_temporary = True

                for operation in operations:
                    if "items_kept" not in operation:
                        need_phase_data = True
                    if "avg_item_size_bytes" not in operation:
                        need_average_sizes = True

            if has_temporary and "memory_limit_bytes" not in system.get("temporary_storage", {}):
                errors.append("Metrica 8: manca system.temporary_storage.memory_limit_bytes.")

            if need_phase_data:
                need_instances(er_schema, entity_stats, 8, errors)
                need_rel_avg(er_schema, relationship_stats, 8, errors)

            if need_average_sizes:
                need_sizes(er_schema, entity_stats, relationship_stats, 8, "avg_size_bytes", errors)
                need_rel_avg(er_schema, relationship_stats, 8, errors)

        elif metric == 9:
            need_sizes(er_schema, entity_stats, relationship_stats, 9, "max_size_bytes", errors)

            for relationship in er_schema.get("relationships", []):
                name = relationship["name"]
                sides = relationship_stats.get(name, {}).get("sides", [])

                if len(sides) != 2:
                    errors.append(f"Metrica 9: mancano le cardinalità massime per '{name}'.")
                    continue

                relationship_definition = None
                for current_relationship in er_schema.get("relationships", []):
                    if current_relationship["name"] == name:
                        relationship_definition = current_relationship
                        break

                for i in range(len(sides)):
                    side = sides[i]
                    if "max_connected" in side or "cardinality_limit" in side:
                        continue

                    er_max = None
                    if relationship_definition is not None:
                        first = relationship_definition["sides"][0]["entity"]
                        second = relationship_definition["sides"][1]["entity"]

                        if first == second:
                            er_max = relationship_definition["sides"][i]["cardinality"]["max"]
                        else:
                            for er_side in relationship_definition["sides"]:
                                if er_side["entity"] == side.get("entity"):
                                    er_max = er_side["cardinality"]["max"]
                                    break

                    if er_max == "N" or er_max is None:
                        errors.append(f"Metrica 9: manca una cardinalità massima per un lato di '{name}'.")

        elif metric == 10:
            need_sizes(er_schema, entity_stats, relationship_stats, 10, "avg_size_bytes", errors)

            if "planning_horizon" not in evaluation:
                errors.append("Metrica 10: manca evaluation.planning_horizon.")

            for relationship in er_schema.get("relationships", []):
                name = relationship["name"]
                for side in relationship_stats.get(name, {}).get("sides", []):
                    if "growth_per_time_unit" not in side and "future_avg_connected" not in side:
                        errors.append(f"Metrica 10: manca la crescita prevista per un lato di '{name}'.")

        elif metric == 11:
            nodes = system.get("distribution", {}).get("nodes")
            if nodes is None:
                errors.append("Metrica 11: manca system.distribution.nodes.")
            elif nodes > 1:
                need_sizes(er_schema, entity_stats, relationship_stats, 11, "avg_size_bytes", errors)

                if frequency_sum(queries) <= 0:
                    errors.append("Metrica 11: la somma delle frequenze delle query deve essere maggiore di 0.")

                for query in queries:
                    if query.get("frequency", 0) <= 0:
                        continue

                    paths = query.get("selection_paths", []) + query.get("projection_paths", [])
                    for path in paths:
                        for step in path[1:]:
                            if "remote_fraction_if_separate" not in step:
                                errors.append(f"Metrica 11: manca remote_fraction_if_separate nella query '{query.get('name')}'.")

        elif metric == 12:
            need_sizes(er_schema, entity_stats, relationship_stats, 12, "avg_size_bytes", errors)

            if "storage_ratio" not in system.get("size_estimates", {}):
                errors.append("Metrica 12: manca system.size_estimates.storage_ratio.")

            replication = system.get("replication", {})
            if "document_replicas" not in replication:
                errors.append("Metrica 12: manca system.replication.document_replicas.")

            if len(indexes) > 0:
                if "index_replicas" not in replication:
                    errors.append("Metrica 12: manca system.replication.index_replicas.")

                for index in indexes:
                    if "participation_fraction" not in index:
                        errors.append(f"Metrica 12: manca participation_fraction per '{index.get('name')}'.")
                    if "avg_entry_storage_bytes" not in index:
                        errors.append(f"Metrica 12: manca avg_entry_storage_bytes per '{index.get('name')}'.")

        elif metric == 13:
            for entity in er_schema.get("entities", []):
                name = entity["name"]
                if "new_instances_per_time_unit" not in entity_stats.get(name, {}):
                    errors.append(f"Metrica 13: manca new_instances_per_time_unit per '{name}'.")

        elif metric == 14:
            if frequency_sum(updates) <= 0:
                errors.append("Metrica 14: la somma delle frequenze degli update deve essere maggiore di 0.")

        elif metric == 15:
            need_sizes(er_schema, entity_stats, relationship_stats, 15, "avg_size_bytes", errors)

            if frequency_sum(updates) <= 0:
                errors.append("Metrica 15: la somma delle frequenze degli update deve essere maggiore di 0.")

            for update in updates:
                if update.get("frequency", 0) <= 0:
                    continue

                if "avg_modified_size_bytes" in update:
                    if update["avg_modified_size_bytes"] <= 0:
                        errors.append(f"Metrica 15: avg_modified_size_bytes deve essere maggiore di 0 per '{update.get('name')}'.")
                elif update.get("operation") != "set_attribute":
                    errors.append(f"Metrica 15: manca avg_modified_size_bytes per '{update.get('name')}'.")
                else:
                    target = update.get("target", {})
                    value = entity_stats.get(target.get("entity"), {}).get("attributes", {}).get(target.get("attribute"), {}).get("avg_size_bytes")
                    if value is not None and value <= 0:
                        errors.append(f"Metrica 15: la dimensione media modificata deve essere maggiore di 0 per '{update.get('name')}'.")

        elif metric == 16:
            if frequency_sum(updates) <= 0:
                errors.append("Metrica 16: la somma delle frequenze degli update deve essere maggiore di 0.")

        elif metric == 17:
            need_instances(er_schema, entity_stats, 17, errors)
            need_rel_avg(er_schema, relationship_stats, 17, errors)
            need_sizes(er_schema, entity_stats, relationship_stats, 17, "avg_size_bytes", errors)

            if "storage_ratio" not in system.get("size_estimates", {}):
                errors.append("Metrica 17: manca system.size_estimates.storage_ratio.")

            for index in indexes:
                if "participation_fraction" not in index:
                    errors.append(f"Metrica 17: manca participation_fraction per '{index.get('name')}'.")
                if "avg_entry_storage_bytes" not in index:
                    errors.append(f"Metrica 17: manca avg_entry_storage_bytes per '{index.get('name')}'.")

            scenario = evaluation.get("lifecycle_scenario")
            if scenario == "migration":
                migration = data_system.get("migration")
                if not isinstance(migration, dict) or migration.get("mode") != "full_rebuild":
                    errors.append("Metrica 17: migration richiede migration.mode = 'full_rebuild'.")
                elif len(migration.get("source_structures", [])) == 0:
                    errors.append("Metrica 17: migration richiede almeno una source_structure.")
            elif scenario != "create":
                errors.append("Metrica 17: manca evaluation.lifecycle_scenario.")

    unique_errors = []
    for error in errors:
        if error not in unique_errors:
            unique_errors.append(error)

    return unique_errors
