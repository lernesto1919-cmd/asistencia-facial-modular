import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [estadisticas, setEstadisticas] = useState({
    total_alumnos: 0,
    total_asistencias: 0
  });

  const [alumnos, setAlumnos] = useState([]);
  const [asistencias, setAsistencias] = useState([]);
  const [grupos, setGrupos] = useState([]);

  const [grupoSeleccionado, setGrupoSeleccionado] = useState("");
  const [mensajeAsistencia, setMensajeAsistencia] = useState("");

  const [formulario, setFormulario] = useState({
    nombre: "",
    matricula: "",
    grupo: "",
    grupo_id: ""
  });

  const [formGrupo, setFormGrupo] = useState({
    nombre: "",
    descripcion: ""
  });

  const cargarDatos = () => {
    fetch("http://127.0.0.1:8000/estadisticas")
      .then(response => response.json())
      .then(data => setEstadisticas(data));

    fetch("http://127.0.0.1:8000/alumnos")
      .then(response => response.json())
      .then(data => setAlumnos(data));

    fetch("http://127.0.0.1:8000/asistencias")
      .then(response => response.json())
      .then(data => setAsistencias(data));

    fetch("http://127.0.0.1:8000/grupos")
      .then(response => response.json())
      .then(data => setGrupos(data));
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const registrarAlumno = (e) => {
    e.preventDefault();

    fetch("http://127.0.0.1:8000/alumnos", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ...formulario,
        grupo_id: Number(formulario.grupo_id)
      })
    })
      .then(response => response.json())
      .then(() => {
        setFormulario({
          nombre: "",
          matricula: "",
          grupo: "",
          grupo_id: ""
        });

        cargarDatos();
      });
  };

  const registrarGrupo = (e) => {
    e.preventDefault();

    fetch("http://127.0.0.1:8000/grupos", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(formGrupo)
    })
      .then(response => response.json())
      .then(() => {
        setFormGrupo({
          nombre: "",
          descripcion: ""
        });

        cargarDatos();
      });
  };

  const iniciarAsistencia = (e) => {
    e.preventDefault();

    fetch("http://127.0.0.1:8000/iniciar-asistencia", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        grupo_id: Number(grupoSeleccionado)
      })
    })
      .then(response => response.json())
      .then(data => {
        setMensajeAsistencia(
          `Asistencia iniciada para grupo ${data.grupo_id}`
        );
      });
  };
  
  const finalizarAsistencia = () => {

  fetch("http://127.0.0.1:8000/finalizar-asistencia", {
    method: "POST"
    })
    .then(response => response.json())
    .then(data => {
      setMensajeAsistencia(data.mensaje);
      setGrupoSeleccionado("");
    });

  };

  return (
    <div className="contenedor">
      <h1 className="titulo">Sistema de Asistencia Facial</h1>

      <div className="tarjetas">
        <div className="tarjeta">
          <h3>Total alumnos</h3>
          <p>{estadisticas.total_alumnos}</p>
        </div>

        <div className="tarjeta">
          <h3>Total asistencias</h3>
          <p>{estadisticas.total_asistencias}</p>
        </div>

        <div className="tarjeta">
          <h3>Total grupos</h3>
          <p>{grupos.length}</p>
        </div>
      </div>

      <div className="seccion">
        <h2>Crear grupo</h2>

        <form className="formulario" onSubmit={registrarGrupo}>
          <input
            type="text"
            placeholder="Nombre del grupo"
            value={formGrupo.nombre}
            onChange={(e) =>
              setFormGrupo({ ...formGrupo, nombre: e.target.value })
            }
          />

          <input
            type="text"
            placeholder="Descripción"
            value={formGrupo.descripcion}
            onChange={(e) =>
              setFormGrupo({ ...formGrupo, descripcion: e.target.value })
            }
          />

          <button type="submit">Guardar grupo</button>
        </form>
      </div>

      <div className="seccion">
        <h2>Grupos registrados</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Grupo</th>
              <th>Descripción</th>
            </tr>
          </thead>

          <tbody>
            {grupos.map(grupo => (
              <tr key={grupo.id}>
                <td>{grupo.id}</td>
                <td>{grupo.nombre}</td>
                <td>{grupo.descripcion}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="seccion">
        <h2>Registrar alumno</h2>

        <form className="formulario" onSubmit={registrarAlumno}>
          <input
            type="text"
            placeholder="Nombre"
            value={formulario.nombre}
            onChange={(e) =>
              setFormulario({ ...formulario, nombre: e.target.value })
            }
          />

          <input
            type="text"
            placeholder="Matrícula"
            value={formulario.matricula}
            onChange={(e) =>
              setFormulario({ ...formulario, matricula: e.target.value })
            }
          />

          <select
            value={formulario.grupo_id}
            onChange={(e) => {
              const grupoSeleccionado = grupos.find(
                grupo => grupo.id === Number(e.target.value)
              );

              setFormulario({
                ...formulario,
                grupo_id: e.target.value,
                grupo: grupoSeleccionado ? grupoSeleccionado.nombre : ""
              });
            }}
          >
            <option value="">Selecciona un grupo</option>

            {grupos.map(grupo => (
              <option key={grupo.id} value={grupo.id}>
                {grupo.nombre}
              </option>
            ))}
          </select>

          <button type="submit">Guardar alumno</button>
        </form>
      </div>

      <div className="seccion">
        <h2>Alumnos registrados</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Matrícula</th>
              <th>Grupo</th>
            </tr>
          </thead>

          <tbody>
            {alumnos.map(alumno => (
              <tr key={alumno.id}>
                <td>{alumno.id}</td>
                <td>{alumno.nombre}</td>
                <td>{alumno.matricula}</td>
                <td>{alumno.nombre_grupo || alumno.grupo}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="seccion">
        <h2>Tomar asistencia</h2>

        <form className="formulario" onSubmit={iniciarAsistencia}>
          <select
            value={grupoSeleccionado}
            onChange={(e) => setGrupoSeleccionado(e.target.value)}
          >
            <option value="">Selecciona un grupo</option>

            {grupos.map(grupo => (
              <option key={grupo.id} value={grupo.id}>
                {grupo.nombre}
              </option>
            ))}
          </select>

          <button type="submit">Iniciar asistencia</button>
          <button type="button" onClick={finalizarAsistencia}>Finalizar asistencia</button>
        </form>

        <p>{mensajeAsistencia}</p>
      </div>

      <div className="seccion">
        <h2>Historial de asistencias</h2>

        <table>
          <thead>
            <tr>
              <th>Alumno</th>
              <th>Fecha</th>
              <th>Hora</th>
            </tr>
          </thead>

          <tbody>
            {asistencias.map(asistencia => (
              <tr key={asistencia.id}>
                <td>{asistencia.nombre}</td>
                <td>{asistencia.fecha}</td>
                <td>{asistencia.hora}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;