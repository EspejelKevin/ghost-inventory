from fastapi import FastAPI, HTTPException, status, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

import sys

from src.container import Container
from src.application import ReserveSeatUseCase, ConfirmPaymentUseCase
from src.infrastructure import SessionLocal, SeatModel


container = Container()


async def startup_event():
    scheduler_adapter = container.task_scheduler()
    scheduler_adapter.scheduler.start()
    print('APScheduler iniciado y conectado a Redis')

async def shutdown_event():
    scheduler_adapter = container.task_scheduler()
    scheduler_adapter.scheduler.shutdown()

    
app = FastAPI(title='Ghost Inventory API', 
              on_startup=[startup_event], on_shutdown=[shutdown_event])


@app.post('/api/v1/seats/{seat_id}/reserve', status_code=status.HTTP_201_CREATED)
@inject
def reserve_seat_endpoint(
    seat_id: int,
    usecase: ReserveSeatUseCase = Depends(Provide[Container.reserve_seat_usecase])
):
    try:
        result = usecase.execute(seat_id)
        return {
            'status': 'Success',
            'message': 'Asiento reservado exitosamente',
            'data': result
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error interno del servidor: {str(e)}')
    

@app.post('/api/v1/reservations/{order_id}/pay', status_code=status.HTTP_201_CREATED)
@inject
def confirm_payment_endpoint(
    order_id: int,
    usecase: ConfirmPaymentUseCase = Depends(Provide[Container.confirm_payment_usecase])
):
    try:
        result = usecase.execute(order_id)
        return {
            'status': 'Success',
            'message': 'Pago procesado exitosamente',
            'data': result
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error interno del servidor: {str(e)}')


class SeatCreate(BaseModel):
    id: int


@app.post('/dev/seats', status_code=status.HTTP_201_CREATED, tags=['development'])
def create_test_seat(seat: SeatCreate):
    db = SessionLocal()
    try:
        db_seat = db.query(SeatModel).filter(SeatModel.id == seat.id).first()
        if db_seat:
            raise HTTPException(status_code=409, detail='El asiento ya existe')
        
        new_seat = SeatModel(id=seat.id, status='DISPONIBLE')
        db.add(new_seat)
        db.commit()
        return {'message': f'Asiento {seat.id} creado como DISPONIBLE'}
    finally:
        db.close()


container.wire(modules=[sys.modules[__name__]])
